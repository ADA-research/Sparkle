"""Tests for recursive_conversion in configspace utilities."""

import ast

from ConfigSpace import ConfigurationSpace
from ConfigSpace.conditions import (
    EqualsCondition,
    GreaterThanCondition,
    InCondition,
    LessThanCondition,
    NotEqualsCondition,
    OrConjunction,
)
from ConfigSpace.forbidden import (
    ForbiddenAndConjunction,
    ForbiddenEqualsClause,
    ForbiddenInClause,
    ForbiddenLessThanRelation,
)
from ConfigSpace.hyperparameters import (
    CategoricalHyperparameter,
    UniformFloatHyperparameter,
    UniformIntegerHyperparameter,
)
import numpy as np
import pytest

from sparkle.tools.configspace import (
    ForbiddenGreaterEqualsClause,
    ForbiddenGreaterThanClause,
    ForbiddenGreaterThanEqualsRelation,
    ForbiddenLessEqualsClause,
    ForbiddenLessThanClause,
    ForbiddenLessThanEqualsRelation,
    ForbiddenOrConjunction,
    expression_to_configspace,
    recursive_conversion,
)


def build_configspace() -> tuple[
    ConfigurationSpace,
    CategoricalHyperparameter,
    UniformIntegerHyperparameter,
    CategoricalHyperparameter,
]:
    """Create a small configspace used across tests."""
    configuration_space = ConfigurationSpace()
    flag = CategoricalHyperparameter("flag", ["on", "off"])
    depth = UniformIntegerHyperparameter("depth", lower=0, upper=10)
    target = CategoricalHyperparameter("mode", ["a", "b"])
    configuration_space.add([flag, depth, target])
    return configuration_space, flag, depth, target


def test_recursive_conversion_in_condition_wraps_string_to_list() -> None:
    """`in` with a bare string should be coerced to a single-value list."""
    configuration_space, flag, _, target = build_configspace()

    condition = expression_to_configspace(
        'flag in "on"', configuration_space, target_parameter=target
    )

    assert isinstance(condition, InCondition)
    assert condition.child == target
    assert condition.parent == flag
    assert condition.values == ["on"]


def test_recursive_conversion_in_condition_casts_iterable_values() -> None:
    """Values in an iterable should be cast to the parent's native type."""
    configuration_space, _, depth, target = build_configspace()

    condition = expression_to_configspace(
        "depth in (1, 2, 3)", configuration_space, target_parameter=target
    )

    assert isinstance(condition, InCondition)
    assert condition.parent == depth
    assert condition.values == [1, 2, 3]
    assert all(isinstance(value, int) for value in condition.values)


def test_recursive_conversion_forbidden_and_conjunction() -> None:
    """Boolean `and` should produce a ForbiddenAndConjunction with the right clauses."""
    configuration_space, flag, depth, _ = build_configspace()
    limit = UniformIntegerHyperparameter("limit", lower=0, upper=10)
    configuration_space.add(limit)

    clause = expression_to_configspace(
        "flag == 'on' and depth < limit", configuration_space
    )

    assert isinstance(clause, ForbiddenAndConjunction)
    relations = []
    for attr in (
        "get_descendant_relations",
        "forbidden_clauses",
        "clauses",
        "_clauses",
    ):
        if callable(getattr(clause, attr, None)):
            relations = list(getattr(clause, attr)())
        else:
            value = getattr(clause, attr, [])
            relations = list(value) if value else relations
        if relations:
            break

    if relations:
        assert any(isinstance(child, ForbiddenEqualsClause) for child in relations)
        assert any(isinstance(child, ForbiddenLessThanRelation) for child in relations)
        equals_clause = next(
            child for child in relations if isinstance(child, ForbiddenEqualsClause)
        )
        lt_clause = next(
            child for child in relations if isinstance(child, ForbiddenLessThanRelation)
        )
        assert equals_clause.hyperparameter == flag
        assert equals_clause.value == "on"
        assert lt_clause.left == depth
        assert lt_clause.right == limit
    else:
        # Rely on repr when internals aren't exposed by this ConfigSpace version.
        clause_repr = repr(clause)
        assert "flag" in clause_repr
        assert "depth" in clause_repr
        assert "<" in clause_repr


def test_recursive_conversion_not_equals_forbidden_raises() -> None:
    """Not-equals is not supported for forbidden clauses; ensure we raise."""
    configuration_space, flag, _, _ = build_configspace()

    with pytest.raises(ValueError):
        expression_to_configspace("flag != 'off'", configuration_space)


def test_expression_to_configspace_parse_error() -> None:
    """Invalid python expression should raise ValueError."""
    configuration_space, _, _, _ = build_configspace()
    with pytest.raises(ValueError):
        expression_to_configspace("flag ==", configuration_space)


def test_recursive_conversion_list_with_multiple_items_raises() -> None:
    """A list of more than one AST element should error."""

    class StubCS:
        def get(self, name: str) -> None:
            return None

        def values(self) -> list[object]:
            return []

    with pytest.raises(ValueError):
        recursive_conversion([ast.Name(id="a"), ast.Name(id="b")], StubCS())


def test_tuple_with_param_name_in_values_raises() -> None:
    """Tuples containing parameter names should raise."""

    class StubCS:
        def __init__(self) -> None:
            self._values = ["foo"]

        def get(self, name: str) -> None:
            return None

        def values(self) -> list[object]:
            return self._values

    tuple_node = ast.Tuple(elts=[ast.Name(id="foo"), ast.Constant(value=1)])
    with pytest.raises(ValueError):
        recursive_conversion(tuple_node, StubCS())


def test_binop_not_supported() -> None:
    """Binary operations should raise NotImplementedError."""

    class StubCS:
        def get(self, name: str) -> None:
            return None

        def values(self) -> list[object]:
            return []

    with pytest.raises(NotImplementedError):
        expression_to_configspace("a + b", StubCS())


def test_bool_or_condition_and_forbidden() -> None:
    """Ensure bool OR builds correct conjunction types."""
    configuration_space, flag, depth, target = build_configspace()
    limit = UniformIntegerHyperparameter("limit", lower=0, upper=10)
    configuration_space.add(limit)
    condition = expression_to_configspace(
        "flag == 'on' or depth < 2", configuration_space, target_parameter=target
    )
    assert isinstance(condition, OrConjunction)
    forbidden = expression_to_configspace(
        "flag == 'on' or depth < limit", configuration_space
    )
    assert isinstance(forbidden, ForbiddenOrConjunction)


def test_unknown_bool_operator_raises() -> None:
    """Manually crafted BoolOp with unknown operator should raise."""

    class StubCS:
        def get(self, name: str) -> None:
            return None

        def values(self) -> list[object]:
            return []

    bool_op = ast.BoolOp(op=ast.Not(), values=[ast.Constant(value=True)])
    with pytest.raises(ValueError):
        recursive_conversion(bool_op, StubCS())


def test_multi_comparison_raises() -> None:
    """Chained comparisons are not supported."""
    configuration_space, _, _, _ = build_configspace()
    with pytest.raises(ValueError):
        expression_to_configspace("1 < 2 < 3", configuration_space)


def test_singleton_iterable_casts_scalar() -> None:
    """Singleton iterables on non-in operators are flattened."""
    configuration_space, _, depth, target = build_configspace()
    condition = expression_to_configspace(
        "depth == (5,)", configuration_space, target_parameter=target
    )
    assert isinstance(condition, EqualsCondition)
    assert condition.value == 5


def test_int_cast_for_right_side() -> None:
    """Ensure int right side casts to parent's native type."""
    configuration_space, _, depth, target = build_configspace()
    condition = expression_to_configspace(
        "depth == 4", configuration_space, target_parameter=target
    )
    assert isinstance(condition, EqualsCondition)
    assert isinstance(condition.value, int)
    assert condition.value == 4


def test_less_equal_and_greater_equal_conditions_errors() -> None:
    """<= and >= should fail for conditions."""
    configuration_space, _, depth, target = build_configspace()
    with pytest.raises(ValueError):
        expression_to_configspace(
            "depth <= 4", configuration_space, target_parameter=target
        )
    with pytest.raises(ValueError):
        expression_to_configspace(
            "depth >= 4", configuration_space, target_parameter=target
        )


def test_comparison_conditions_and_forbiddens() -> None:
    """Cover remaining comparison branches."""
    configuration_space, flag, depth, target = build_configspace()
    lt_cond = expression_to_configspace(
        "depth < 3", configuration_space, target_parameter=target
    )
    assert isinstance(lt_cond, LessThanCondition)
    gt_cond = expression_to_configspace(
        "depth > 3", configuration_space, target_parameter=target
    )
    assert isinstance(gt_cond, GreaterThanCondition)
    eq_forbidden = expression_to_configspace("flag == 'on'", configuration_space)
    assert isinstance(eq_forbidden, ForbiddenEqualsClause)
    in_forbidden = expression_to_configspace(
        "flag in ['on', 'off']", configuration_space
    )
    assert isinstance(in_forbidden, ForbiddenInClause)
    neq_cond = expression_to_configspace(
        "flag != 'off'", configuration_space, target_parameter=target
    )
    assert isinstance(neq_cond, NotEqualsCondition)


def test_notin_and_is_operators_raise() -> None:
    """Unsupported operators should raise."""
    configuration_space, _, _, _ = build_configspace()
    with pytest.raises(ValueError):
        expression_to_configspace("1 not in [1,2]", configuration_space)
    with pytest.raises(NotImplementedError):
        expression_to_configspace("a is b", configuration_space)
    with pytest.raises(NotImplementedError):
        expression_to_configspace("a is not b", configuration_space)


def test_fallback_unsupported_type_raises() -> None:
    """Unknown AST node should raise ValueError."""

    class StubCS:
        def get(self, name: str) -> None:
            return None

        def values(self) -> list[object]:
            return []

    node = ast.IfExp(
        test=ast.Constant(value=True),
        body=ast.Constant(value=1),
        orelse=ast.Constant(value=2),
    )
    with pytest.raises(ValueError):
        recursive_conversion(node, StubCS())


def test_forbidden_relations_with_vectors() -> None:
    """Exercise is_forbidden methods for custom forbidden relations."""
    hp_a = UniformIntegerHyperparameter("a", lower=0, upper=10, default_value=0)
    hp_b = UniformIntegerHyperparameter("b", lower=0, upper=10, default_value=0)
    lt_eq = ForbiddenLessThanEqualsRelation(left=hp_a, right=hp_b)
    lt_eq.vector_ids = [0, 1]
    assert "a <=" in repr(lt_eq)
    assert lt_eq.is_forbidden_value({"a": 1, "b": 2}) is True
    assert lt_eq.is_forbidden_value({"a": 3, "b": 2}) is False
    assert lt_eq.is_forbidden_vector(np.array([1.0, 1.0])) is True
    assert lt_eq.is_forbidden_vector(np.array([2.0, 1.0])) is False
    arr = np.array([[1.0, 1.5], [2.0, 2.0]])
    mask = lt_eq.is_forbidden_vector_array(arr)
    assert mask.tolist() == [True, True]

    gt_eq = ForbiddenGreaterThanEqualsRelation(left=hp_a, right=hp_b)
    gt_eq.vector_ids = [0, 1]
    assert "a >=" in repr(gt_eq)
    assert gt_eq.is_forbidden_value({"a": 2, "b": 1}) is True
    assert gt_eq.is_forbidden_vector(np.array([2.0, 3.0])) is False
    arr = np.array([[2.0, 3.0], [1.0, 2.0]])
    mask = gt_eq.is_forbidden_vector_array(arr)
    assert mask.tolist() == [True, True]


def test_forbidden_clauses_greater_less_variants() -> None:
    """Cover clause subclasses and their helpers."""
    hp_c = UniformFloatHyperparameter("c", lower=0.0, upper=10.0, default_value=0.0)

    gt_clause = ForbiddenGreaterThanClause(hyperparameter=hp_c, value=2.0)
    gt_clause.vector_id = 0
    gt_clause.vector_value = 2.0
    assert ">" in repr(gt_clause)
    assert gt_clause.is_forbidden_value({"c": 3.0}) is True
    assert bool(gt_clause.is_forbidden_vector(np.array([1.0]))) is False
    assert gt_clause.is_forbidden_vector_array(np.array([[1.0, 3.0]])).tolist() == [
        False,
        True,
    ]
    assert gt_clause.to_dict()["type"] == "GREATER"

    gte_clause = ForbiddenGreaterEqualsClause(hyperparameter=hp_c, value=2.0)
    gte_clause.vector_id = 0
    gte_clause.vector_value = 2.0
    assert ">=" in repr(gte_clause)
    assert gte_clause.is_forbidden_value({"c": 2.0}) is True
    assert bool(gte_clause.is_forbidden_vector(np.array([2.0]))) is True
    assert gte_clause.is_forbidden_vector_array(np.array([[1.0, 2.0]])).tolist() == [
        False,
        True,
    ]
    assert gte_clause.to_dict()["type"] == "GREATEREQUAL"

    lt_clause = ForbiddenLessThanClause(hyperparameter=hp_c, value=2.0)
    lt_clause.vector_id = 0
    lt_clause.vector_value = 2.0
    assert "<" in repr(lt_clause)
    assert lt_clause.is_forbidden_value({"c": 1.0}) is True
    assert bool(lt_clause.is_forbidden_vector(np.array([1.0]))) is True
    assert lt_clause.is_forbidden_vector_array(np.array([[1.0, 3.0]])).tolist() == [
        True,
        False,
    ]
    assert lt_clause.to_dict()["type"] == "LESS"

    lte_clause = ForbiddenLessEqualsClause(hyperparameter=hp_c, value=2.0)
    lte_clause.vector_id = 0
    lte_clause.vector_value = 2.0
    assert "<=" in repr(lte_clause)
    assert lte_clause.is_forbidden_value({"c": 2.0}) is True
    assert bool(lte_clause.is_forbidden_vector(np.array([3.0]))) is False
    assert lte_clause.is_forbidden_vector_array(np.array([[1.0, 2.0]])).tolist() == [
        False,
        True,
    ]
    assert lte_clause.to_dict()["type"] == "LESSEQUAL"


def test_forbidden_or_conjunction_behaviour() -> None:
    """Validate ForbiddenOrConjunction helpers."""
    hp_a = UniformIntegerHyperparameter("a", lower=0, upper=10, default_value=0)
    hp_b = UniformIntegerHyperparameter("b", lower=0, upper=10, default_value=0)
    eq_clause = ForbiddenEqualsClause(hyperparameter=hp_a, value=1)
    eq_clause.vector_id = 0
    eq_clause.vector_value = 1
    lt_clause = ForbiddenLessThanClause(hyperparameter=hp_b, value=2)
    lt_clause.vector_id = 1
    lt_clause.vector_value = 2

    conj = ForbiddenOrConjunction(eq_clause, lt_clause)
    assert "||" in repr(conj)
    assert conj.is_forbidden_value({"a": 1, "b": 5}) is True
    assert conj.is_forbidden_value({"a": 0, "b": 1}) is True
    assert conj.is_forbidden_value({"a": 0, "b": 5}) is False

    vec = np.array([1.0, 3.0])
    lt_vector_clause = ForbiddenLessThanRelation(left=hp_b, right=hp_a)
    lt_vector_clause.vector_ids = [1, 0]
    conj_vectors = ForbiddenOrConjunction(eq_clause, lt_vector_clause)
    assert conj_vectors.is_forbidden_vector(vec) is True
    arr = np.array([[1.0, 0.0], [0.0, 3.0]])
    mask = conj_vectors.is_forbidden_vector_array(arr)
    assert mask.tolist() == [True, False]
    as_dict = conj.to_dict()
    assert as_dict["type"] == "OR"
    assert len(as_dict["clauses"]) == 2
