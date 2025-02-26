"""Extensions of the ConfigSpace lib."""
from __future__ import annotations
from typing_extensions import override, Iterable
import ast

import numpy as np
from typing import Any
from ConfigSpace import ConfigurationSpace
from ConfigSpace.hyperparameters import Hyperparameter
from ConfigSpace.types import Array, Mask, f64

from ConfigSpace.conditions import (
    Condition,
    AndConjunction,
    OrConjunction,
    EqualsCondition,
    GreaterThanCondition,
    InCondition,
    LessThanCondition,
    NotEqualsCondition
)

from ConfigSpace.forbidden import (
    ForbiddenGreaterThanRelation,
    ForbiddenLessThanRelation,
    ForbiddenClause,
    ForbiddenConjunction,
    ForbiddenRelation,
    ForbiddenInClause,
    ForbiddenEqualsClause,
    ForbiddenAndConjunction
)

_SENTINEL = object()


def expression_to_configspace(
        expression: str | ast.Module,
        configspace: ConfigurationSpace,
        target_parameter: Hyperparameter = None) -> ForbiddenClause | Condition:
    """Convert a logic expression to ConfigSpace expression.

    Args:
        expression: The expression to convert.
        configspace: The ConfigSpace to use.
        target_parameter: For conditions, will parse the expression as a condition
            underwhich the parameter will be active.
    """
    if isinstance(expression, str):
        try:
            expression = ast.parse(expression)
        except Exception as e:
            raise ValueError(f"Could not parse expression: '{expression}', {e}")
    if isinstance(expression, ast.Module):
        expression = expression.body[0]
    return recursive_conversion(expression, configspace,
                                target_parameter=target_parameter)


def recursive_conversion(
        item: ast.mod,
        configspace: ConfigurationSpace,
        target_parameter: Hyperparameter = None) -> ForbiddenClause | Condition:
    """Recursively parse the AST tree to a ConfigSpace expression.

    Args:
        item: The item to parse.
        configspace: The ConfigSpace to use.
        target_parameter: For conditions, will parse the expression as a condition
            underwhich the parameter will be active.

    Returns:
        A ConfigSpace expression
    """
    if isinstance(item, list):
        if len(item) > 1:
            raise ValueError(f"Can not parse list of elements: {item}.")
        item = item[0]
    if isinstance(item, ast.Expr):
        return recursive_conversion(item.value, configspace, target_parameter)
    if isinstance(item, ast.Name):  # Convert to hyperparameter
        hp = configspace.get(item.id)
        return hp if hp is not None else item.id
    if isinstance(item, ast.Constant):
        return item.value
    if (isinstance(item, ast.Tuple)
            or isinstance(item, ast.Set) or isinstance(item, ast.List)):
        values = []
        for v in item.elts:
            if isinstance(v, ast.Constant):
                values.append(v.value)
            elif isinstance(v, ast.Name):  # Check if its a parameter
                if v.id in list(configspace.values()):
                    raise ValueError("Only constants allowed in tuples. "
                                     f"Found: {item.elts}")
                values.append(v.id)  # String value was interpreted as parameter
        return values
    if isinstance(item, ast.BinOp):
        raise NotImplementedError("Binary operations not supported by ConfigSpace.")
    if isinstance(item, ast.BoolOp):
        values = [recursive_conversion(v, configspace, target_parameter)
                  for v in item.values]
        if isinstance(item.op, ast.Or):
            if target_parameter:
                return OrConjunction(*values)
            return ForbiddenOrConjunction(*values)
        elif isinstance(item.op, ast.And):
            if target_parameter:
                return AndConjunction(*values)
            return ForbiddenAndConjunction(*values)
        else:
            raise ValueError(f"Unknown boolean operator: {item.op}")
    if isinstance(item, ast.Compare):
        if len(item.ops) > 1:
            raise ValueError(f"Only single comparisons allowed. Found: {item.ops}")
        left = recursive_conversion(item.left, configspace, target_parameter)
        right = recursive_conversion(item.comparators, configspace, target_parameter)
        operator = item.ops[0]
        if isinstance(left, Hyperparameter):  # Convert to HP type
            if isinstance(right, Iterable) and not isinstance(right, str):
                right = [type(left.default_value)(v) for v in right]
                if len(right) == 1 and not isinstance(operator, ast.In):
                    right = right[0]
            elif isinstance(right, int):
                right = type(left.default_value)(right)

        if isinstance(operator, ast.Lt):
            if target_parameter:
                return LessThanCondition(target_parameter, left, right)
            return ForbiddenLessThanRelation(left=left, right=right)
        if isinstance(operator, ast.LtE):
            if target_parameter:
                raise ValueError("LessThanEquals not supported for conditions.")
            return ForbiddenLessThanEqualsRelation(left=left, right=right)
        if isinstance(operator, ast.Gt):
            if target_parameter:
                return GreaterThanCondition(target_parameter, left, right)
            return ForbiddenGreaterThanRelation(left=left, right=right)
        if isinstance(operator, ast.GtE):
            if target_parameter:
                raise ValueError("GreaterThanEquals not supported for conditions.")
            return ForbiddenGreaterThanEqualsRelation(left=left, right=right)
        if isinstance(operator, ast.Eq):
            if target_parameter:
                return EqualsCondition(target_parameter, left, right)
            return ForbiddenEqualsClause(hyperparameter=left, value=right)
        if isinstance(operator, ast.In):
            if target_parameter:
                return InCondition(target_parameter, left, right)
            return ForbiddenInClause(hyperparameter=left, values=right)
        if isinstance(operator, ast.NotEq):
            if target_parameter:
                return NotEqualsCondition(target_parameter, left, right)
            raise ValueError("NotEq operator not supported for ForbiddenClauses.")
        # The following classes do not (yet?) exist in configspace
        if isinstance(operator, ast.NotIn):
            raise ValueError("NotIn operator not supported for ForbiddenClauses.")
        if isinstance(operator, ast.Is):
            raise NotImplementedError("Is operator not supported.")
        if isinstance(operator, ast.IsNot):
            raise NotImplementedError("IsNot operator not supported.")
    raise ValueError(f"Unsupported type: {item}")


class ForbiddenLessThanEqualsRelation(ForbiddenLessThanRelation):
    """A ForbiddenLessThanEquals relation between two hyperparameters."""

    _RELATION_STR = "LESSEQUAL"

    def __repr__(self: ForbiddenLessThanEqualsRelation) -> str:
        """Return a string representation of the ForbiddenLessThanEqualsRelation."""
        return f"Forbidden: {self.left.name} <= {self.right.name}"

    @override
    def is_forbidden_value(self: ForbiddenLessThanEqualsRelation,
                           values: dict[str, Any]) -> bool:
        """Check if the value is forbidden."""
        # Relation is always evaluated against actual value and not vector rep
        left = values.get(self.left.name, _SENTINEL)
        if left is _SENTINEL:
            return False

        right = values.get(self.right.name, _SENTINEL)
        if right is _SENTINEL:
            return False

        return left <= right  # type: ignore

    @override
    def is_forbidden_vector(self: ForbiddenLessThanEqualsRelation,
                            vector: Array[f64]) -> bool:
        """Check if the vector is forbidden."""
        # Relation is always evaluated against actual value and not vector rep
        left: f64 = vector[self.vector_ids[0]]  # type: ignore
        right: f64 = vector[self.vector_ids[1]]  # type: ignore
        if np.isnan(left) or np.isnan(right):
            return False
        return self.left.to_value(left) <= self.right.to_value(right)  # type: ignore

    @override
    def is_forbidden_vector_array(self: ForbiddenLessThanEqualsRelation,
                                  arr: Array[f64]) -> Mask:
        """Check if the vector array is forbidden."""
        left = arr[self.vector_ids[0]]
        right = arr[self.vector_ids[1]]
        valid = ~(np.isnan(left) | np.isnan(right))
        out = np.zeros_like(valid)
        out[valid] = self.left.to_value(left[valid]) <= self.right.to_value(right[valid])
        return out


class ForbiddenGreaterThanEqualsRelation(ForbiddenGreaterThanRelation):
    """A ForbiddenGreaterThanEquals relation between two hyperparameters."""

    _RELATION_STR = "GREATEREQUAL"

    def __repr__(self: ForbiddenGreaterThanEqualsRelation) -> str:
        """Return a string representation of the ForbiddenGreaterThanEqualsRelation."""
        return f"Forbidden: {self.left.name} >= {self.right.name}"

    @override
    def is_forbidden_value(self: ForbiddenGreaterThanEqualsRelation,
                           values: dict[str, Any]) -> bool:
        """Check if the value is forbidden."""
        left = values.get(self.left.name, _SENTINEL)
        if left is _SENTINEL:
            return False

        right = values.get(self.right.name, _SENTINEL)
        if right is _SENTINEL:
            return False

        return left >= right  # type: ignore

    @override
    def is_forbidden_vector(self: ForbiddenGreaterThanEqualsRelation,
                            vector: Array[f64]) -> bool:
        """Check if the vector is forbidden."""
        # Relation is always evaluated against actual value and not vector rep
        left: f64 = vector[self.vector_ids[0]]  # type: ignore
        right: f64 = vector[self.vector_ids[1]]  # type: ignore
        if np.isnan(left) or np.isnan(right):
            return False
        return self.left.to_value(left) >= self.right.to_value(right)  # type: ignore

    @override
    def is_forbidden_vector_array(self: ForbiddenGreaterThanEqualsRelation,
                                  arr: Array[f64]) -> Mask:
        """Check if the vector array is forbidden."""
        left = arr[self.vector_ids[0]]
        right = arr[self.vector_ids[1]]
        valid = ~(np.isnan(left) | np.isnan(right))
        out = np.zeros_like(valid)
        out[valid] = self.left.to_value(left[valid]) >= self.right.to_value(right[valid])
        return out


class ForbiddenGreaterThanClause(ForbiddenEqualsClause):
    """A ForbiddenGreaterThanClause.

    It forbids a value from the value range of a hyperparameter to be
    *greater than* `value`.

    Forbids the value of the hyperparameter *a* to be greater than 2

    Args:
        hyperparameter: Methods on which a restriction will be made
        value: forbidden value
    """

    def __repr__(self: ForbiddenGreaterThanClause) -> str:
        """Return a string representation of the ForbiddenGreaterThanClause."""
        return f"Forbidden: {self.hyperparameter.name} > {self.value!r}"

    @override
    def is_forbidden_value(self: ForbiddenGreaterThanClause,
                           values: dict[str, Any]) -> bool:
        """Check if the value is forbidden."""
        return (  # type: ignore
            values.get(self.hyperparameter.name, _SENTINEL) > self.value
        )

    @override
    def is_forbidden_vector(self: ForbiddenGreaterThanClause,
                            vector: Array[f64]) -> bool:
        """Check if the vector is forbidden."""
        return vector[self.vector_id] > self.vector_value  # type: ignore

    @override
    def is_forbidden_vector_array(self: ForbiddenGreaterThanClause,
                                  arr: Array[f64]) -> Mask:
        """Check if the vector array is forbidden."""
        return np.greater(arr[self.vector_id], self.vector_value, dtype=np.bool_)

    @override
    def to_dict(self: ForbiddenGreaterThanClause) -> dict[str, Any]:
        """Convert the ForbiddenGreaterThanClause to a dictionary."""
        return {
            "name": self.hyperparameter.name,
            "type": "GREATER",
            "value": self.value,
        }


class ForbiddenGreaterEqualsClause(ForbiddenEqualsClause):
    """A ForbiddenGreaterEqualsClause.

    It forbids a value from the value range of a hyperparameter to be
    *greater or equal to* `value`.

    Forbids the value of the hyperparameter *a* to be greater or equal to 2

    Args:
        hyperparameter: Methods on which a restriction will be made
        value: forbidden value
    """

    def __repr__(self: ForbiddenGreaterEqualsClause) -> str:
        """Return a string representation of the ForbiddenGreaterEqualsClause."""
        return f"Forbidden: {self.hyperparameter.name} >= {self.value!r}"

    @override
    def is_forbidden_value(self: ForbiddenGreaterEqualsClause,
                           values: dict[str, Any]) -> bool:
        """Check if the value is forbidden."""
        return (  # type: ignore
            values.get(self.hyperparameter.name, _SENTINEL) >= self.value
        )

    @override
    def is_forbidden_vector(self: ForbiddenGreaterEqualsClause,
                            vector: Array[f64]) -> bool:
        """Check if the vector is forbidden."""
        return vector[self.vector_id] >= self.vector_value  # type: ignore

    @override
    def is_forbidden_vector_array(self: ForbiddenGreaterEqualsClause,
                                  arr: Array[f64]) -> Mask:
        """Check if the vector array is forbidden."""
        return np.greater_equal(arr[self.vector_id], self.vector_value, dtype=np.bool_)

    @override
    def to_dict(self: ForbiddenGreaterEqualsClause) -> dict[str, Any]:
        """Convert the ForbiddenGreaterEqualsClause to a dictionary."""
        return {
            "name": self.hyperparameter.name,
            "type": "GREATEREQUAL",
            "value": self.value,
        }


class ForbiddenLessThanClause(ForbiddenEqualsClause):
    """A ForbiddenLessThanClause.

    It forbids a value from the value range of a hyperparameter to be
    *less than* `value`.

    Args:
        hyperparameter: Methods on which a restriction will be made
        value: forbidden value
    """

    def __repr__(self: ForbiddenLessThanClause) -> str:
        """Return a string representation of the ForbiddenLessThanClause."""
        return f"Forbidden: {self.hyperparameter.name} < {self.value!r}"

    @override
    def is_forbidden_value(self: ForbiddenLessThanClause,
                           values: dict[str, Any]) -> bool:
        """Check if the value is forbidden."""
        return (  # type: ignore
            values.get(self.hyperparameter.name, _SENTINEL) < self.value
        )

    @override
    def is_forbidden_vector(self: ForbiddenLessThanClause, vector: Array[f64]) -> bool:
        """Check if the vector is forbidden."""
        return vector[self.vector_id] < self.vector_value  # type: ignore

    @override
    def is_forbidden_vector_array(self: ForbiddenLessThanClause,
                                  arr: Array[f64]) -> Mask:
        """Check if the vector array is forbidden."""
        return np.less(arr[self.vector_id], self.vector_value, dtype=np.bool_)

    @override
    def to_dict(self: ForbiddenLessThanClause) -> dict[str, Any]:
        """Convert the ForbiddenLessThanClause to a dictionary."""
        return {
            "name": self.hyperparameter.name,
            "type": "LESS",
            "value": self.value,
        }


class ForbiddenLessEqualsClause(ForbiddenEqualsClause):
    """A ForbiddenLessEqualsClause.

    It forbids a value from the value range of a hyperparameter to be
    *less or equal to* `value`.

    Args:
        hyperparameter: Methods on which a restriction will be made
        value: forbidden value
    """

    def __repr__(self: ForbiddenLessEqualsClause) -> str:
        """Return a string representation of the ForbiddenLessEqualsClause."""
        return f"Forbidden: {self.hyperparameter.name} <= {self.value!r}"

    @override
    def is_forbidden_value(self: ForbiddenLessEqualsClause,
                           values: dict[str, Any]) -> bool:
        """Check if the value is forbidden."""
        return (  # type: ignore
            values.get(self.hyperparameter.name, _SENTINEL) <= self.value
        )

    @override
    def is_forbidden_vector(self: ForbiddenLessEqualsClause, vector: Array[f64]) -> bool:
        """Check if the vector is forbidden."""
        return vector[self.vector_id] <= self.vector_value  # type: ignore

    @override
    def is_forbidden_vector_array(self: ForbiddenLessEqualsClause,
                                  arr: Array[f64]) -> Mask:
        """Check if the vector array is forbidden."""
        return np.greater_equal(arr[self.vector_id], self.vector_value, dtype=np.bool_)

    @override
    def to_dict(self: ForbiddenLessEqualsClause) -> dict[str, Any]:
        """Convert the ForbiddenLessEqualsClause to a dictionary."""
        return {
            "name": self.hyperparameter.name,
            "type": "LESSEQUAL",
            "value": self.value,
        }


class ForbiddenOrConjunction(ForbiddenConjunction):
    """A ForbiddenOrConjunction.

    The ForbiddenOrConjunction combines forbidden-clauses, which allows to
    build powerful constraints.

    ```python exec="true", source="material-block" result="python"
    from ConfigSpace import (
        ConfigurationSpace,
        ForbiddenEqualsClause,
        ForbiddenInClause,
    )
    from sparkle.tools.configspace import ForbiddenOrConjunction

    cs = ConfigurationSpace({"a": [1, 2, 3], "b": [2, 5, 6]})
    forbidden_clause_a = ForbiddenEqualsClause(cs["a"], 2)
    forbidden_clause_b = ForbiddenInClause(cs["b"], [2])

    forbidden_clause = ForbiddenOrConjunction(forbidden_clause_a, forbidden_clause_b)

    cs.add(forbidden_clause)
    print(cs)
    ```

    Args:
        *args: forbidden clauses, which should be combined
    """

    components: tuple[ForbiddenClause | ForbiddenConjunction | ForbiddenRelation, ...]
    """Components of the conjunction."""

    dlcs: tuple[ForbiddenClause | ForbiddenRelation, ...]
    """Descendant literal clauses of the conjunction.

    These are the base forbidden clauses/relations that are part of conjunctions.

    !!! note

        This will only store a unique set of the descendant clauses, no duplicates.
    """

    def __repr__(self: ForbiddenOrConjunction) -> str:
        """Return a string representation of the ForbiddenOrConjunction."""
        return "(" + " || ".join([str(c) for c in self.components]) + ")"

    @override
    def is_forbidden_value(self: ForbiddenOrConjunction, values: dict[str, Any]) -> bool:
        """Check if the value is forbidden."""
        return any([forbidden.is_forbidden_value(values)
                    for forbidden in self.components])

    @override
    def is_forbidden_vector(self: ForbiddenOrConjunction, vector: Array[f64]) -> bool:
        """Check if the vector is forbidden."""
        return any(
            forbidden.is_forbidden_vector(vector) for forbidden in self.components
        )

    @override
    def is_forbidden_vector_array(self: ForbiddenOrConjunction, arr: Array[f64]) -> Mask:
        """Check if the vector array is forbidden."""
        forbidden_mask: Mask = np.zeros(shape=arr.shape[1], dtype=np.bool_)
        for forbidden in self.components:
            forbidden_mask |= forbidden.is_forbidden_vector_array(arr)

        return forbidden_mask

    @override
    def to_dict(self: ForbiddenOrConjunction) -> dict[str, Any]:
        """Convert the ForbiddenOrConjunction to a dictionary."""
        return {
            "type": "OR",
            "clauses": [component.to_dict() for component in self.components],
        }
