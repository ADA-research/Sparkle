"""The Parameter Configuration Space Parser class."""
from __future__ import annotations
import re
import sys
import ast
import ConfigSpace.conditions
import ConfigSpace.forbidden
import ConfigSpace.hyperparameters
import numpy as np
from enum import Enum
from abc import ABC
from pathlib import Path

import tabulate
import ConfigSpace
from ConfigSpace import ConfigurationSpace
from sparkle.tools.configspace import expression_to_configspace


class PCSConvention(Enum):
    """Internal pcs convention enum."""
    unknown = ""
    SMAC = "smac"
    ParamILS = "paramils"
    IRACE = "irace"
    ConfigSpace = "configspace"


class PCSObject(ABC):
    """General data structure to keep the pcs file in.

    Fields are added by functions, such that checks can be conducted.
    """
    def __init__(self: PCSObject) -> None:
        """Initialize the PCSObject."""
        self.params = []

    def add_param(self: PCSObject,
                  name: str,
                  structure: str = "integer",
                  domain: list = [-sys.maxsize, sys.maxsize],
                  scale: str = "linear",
                  default: str = "0",
                  comment: str = None) -> None:
        """Add a parameter to the PCSObject."""
        if structure not in ["integer", "real", "categorical", "ordinal"]:
            raise ValueError(f"Parameter structure {structure} not supported.")

        # Domain check
        if structure in ["integer", "real"]:
            if len(domain) != 2:
                raise ValueError(f"Parameter domain {domain} not supported.")
            pass
        elif structure == "categorical":
            # TODO: check categories
            scale = None

        self.params.append({
            "name": name,
            "structure": structure,
            "domain": domain,
            "scale": scale,
            "default": default,
            "comment": comment,
            "type": "parameter",
        })

    def add_constraint(self: PCSObject, **kwargs: any) -> None:
        """Add a constraint to the PCSObject."""
        # TODO add checks
        self.params.append({**kwargs, "type": "constraint"})

    def add_forbidden(self: PCSObject, **kwargs: any) -> None:
        """Add a forbidden clause to the PCSObject."""
        # TODO add checks
        self.params.append({**kwargs, "type": "forbidden"})

    def add_comment(self: PCSObject, **kwargs: any) -> None:
        """Add a comment to the PCSObject."""
        # TODO add checks
        self.params.append({**kwargs, "type": "comment"})

    def clear(self: PCSObject) -> None:
        """Clear the PCSObject."""
        self.params = []

    def get(self: PCSObject, name: str) -> dict:
        """Get a parameter from the PCSObject based on the name."""
        names = {p["name"]: i for i, p in enumerate(self.params) if "name" in p}
        if name in names:
            return self.params[names[name]]
        return None


class PCSConverter:
    """Parser class independent file of notation."""
    section_regex = re.compile(r"^\[[a-zA-Z]+\]")

    smac2_params_regex = re.compile(r"^(?P<name>[a-zA-Z0-9_]+)\s+(?P<type>[a-zA-Z]+)\s+"
                                    r"(?P<values>[a-zA-Z0-9 \[\]{}_,. ]+)\s+"
                                    r"\[(?P<default>[a-zA-Z0-9._-]+)\]?\s*"
                                    r"(?P<scale>log)?\s*(?P<comment>#.*)?$")
    smac2_conditions_regex = re.compile(r"^(?P<parameter>[a-zA-Z0-9_]+)\s*\|\s*"
                                        r"(?P<expression>.+)$")
    smac2_forbidden_regex = re.compile(r"\{(?P<forbidden>.+)\}$")

    irace_params_regex = re.compile(r"^(?P<name>[a-zA-Z0-9_]+)\s+"
                                    r"(?P<switch>[\"a-zA-Z0-9_\- ]+)\s+"
                                    r"(?P<type>[cir])\s+"
                                    r"(?P<values>[a-zA-Z0-9()_,. ]+)\s*"
                                    r"\|?(?P<conditions>.+)?$")
    irace_forbidden_regex = re.compile(r"")

    @staticmethod
    def parse(file: Path) -> ConfigurationSpace:
        """Determines the format of a pcs file and parses into Configuration Space."""
        if file.suffix == ".yaml":
            return ConfigSpace.ConfigurationSpace.from_yaml(file)
        if file.suffix == ".json":
            return ConfigSpace.ConfigurationSpace.from_json(file)

        file_contents = file.open().readlines()
        for line in file_contents:
            if line.startswith("#"):  # Comment line
                continue
            if "#" in line:
                line, _ = line.split("#", maxsplit=1)
            if re.match(PCSConverter.smac2_params_regex, line):
                return PCSConverter.parse_smac(file_contents)
            elif re.match(PCSConverter.irace_params_regex, line):
                return PCSConverter.parse_irace(file_contents)

        raise Exception(
            f"PCS convention not recognised based on line:\n{line}")

    @staticmethod
    def parse_smac(content: list[str] | Path) -> ConfigurationSpace:
        """Parses a smac file."""
        content = content.open().readlines() if isinstance(content, Path) else content
        cs = ConfigurationSpace()
        for line in content:
            if not line.strip() or line.startswith("#"):  # Empty or comment
                continue
            comment = None
            line = line.strip()
            if re.match(PCSConverter.smac2_params_regex, line):
                parameter = re.fullmatch(PCSConverter.smac2_params_regex, line)
                name = parameter.group("name")
                parameter_type = parameter.group("type")
                values = parameter.group("values")
                default = parameter.group("default")
                comment = parameter.group("comment")
                scale = parameter.group("scale")
                if parameter_type == "integer":
                    values = ast.literal_eval(values)
                    csparam = ConfigSpace.UniformIntegerHyperparameter(
                        name=name,
                        lower=int(values[0]),
                        upper=int(values[1]),
                        default_value=int(default),
                        log=scale == "log",
                        meta=comment,
                    )
                elif parameter_type == "real":
                    values = ast.literal_eval(values)
                    csparam = ConfigSpace.UniformFloatHyperparameter(
                        name=name,
                        lower=float(values[0]),
                        upper=float(values[1]),
                        default_value=float(default),
                        log=scale == "log",
                        meta=comment,
                    )
                elif parameter_type == "categorical":
                    values = [str(i) for i in ast.literal_eval(values)]
                    csparam = ConfigSpace.CategoricalHyperparameter(
                        name=name,
                        choices=values,
                        default_value=default,
                        meta=comment,
                        # Does not seem to contain any weights?
                    )
                elif parameter_type == "ordinal":
                    values = [str(i) for i in ast.literal_eval(values)]
                    csparam = ConfigSpace.OrdinalHyperparameter(
                        name=name,
                        sequence=values,
                        default_value=default,
                        meta=comment,
                    )
                cs.add(csparam)
            elif re.match(PCSConverter.smac2_conditions_regex, line):
                # Break up the expression into the smallest possible pieces
                match = re.fullmatch(PCSConverter.smac2_conditions_regex, line)
                parameter, condition =\
                    match.group("parameter"), match.group("expression")
                parameter = cs[parameter.strip()]
                condition = condition.replace(" || ", " or ").replace(" && ", " and ")
                condition = re.sub(r"(?<![<>!])=", "==", condition)
                condition = re.sub(r"!==", "!=", condition)
                condition = expression_to_configspace(condition, cs,
                                                      target_parameter=parameter)
                cs.add(condition)
            elif re.match(PCSConverter.smac2_forbidden_regex, line):
                match = re.fullmatch(PCSConverter.smac2_forbidden_regex, line)
                forbidden = match.group("forbidden")
                # Forbidden expressions structure <expression> <operator> <value>
                # where expressions can contain:
                # Logical Operators: >=, <=, >, <, ==, !=,
                # Logical clause operators: ( ), ||, &&,
                # Supported by SMAC2 but not by ConfigSpace?:
                # Arithmetic Operators: +, -, *, ^, %
                # Functions: abs, acos, asin, atan, cbrt, ceil, cos, cosh, exp, floor,
                # log, log10, log2, sin, sinh, sqrt, tan, tanh
                rejected_operators = ("+", "-", "*", "^", "%",
                                      "abs", "acos", "asin", "atan", "cbrt", "ceil",
                                      "cos", "cosh", "exp", "floor", "log", "log10",
                                      "log2", "sin", "sinh", "sqrt", "tan", "tanh")
                if any([r in forbidden.split(" ") for r in rejected_operators]):
                    print("WARNING: Arithmetic operators are not supported by "
                          "ConfigurationSpace. Skipping forbidden expression:\n"
                          f"{forbidden}")
                    continue
                forbidden = forbidden.replace(" && ", " and ").replace(
                    ", ", " and ").replace(" || ", " or ").strip()  # To AST notation
                forbidden = re.sub(r"(?<![<>!])=", "==", forbidden)
                forbidden = expression_to_configspace(forbidden, cs)
                cs.add(forbidden)
            else:
                raise Exception(
                    f"SMAC2 PCS expression not recognised on line:\n{line}")
        return cs

    @staticmethod
    def parse_irace(content: list[str] | Path) -> ConfigurationSpace:
        """Parses a irace file."""
        name = content.name if isinstance(content, Path) else "irace"
        content = content.open().readlines() if isinstance(content, Path) else content
        cs = ConfigurationSpace(name=name)
        for line in content:
            if not line.strip() or line.startswith("#"):  # Empty or comment
                continue
            if re.match(PCSConverter.irace_params_regex, line):
                # TODO: Parse different types of parameters
                pass
            elif re.match(PCSConverter.irace_forbidden_regex, line):
                pass
            else:
                raise Exception(
                    f"IRACE PCS expression not recognised on line:\n{line}")
        return cs

    @staticmethod
    def export(configspace: ConfigurationSpace,
               format: PCSConvention, file: Path) -> None:
        """Exports a config space object to a specific PCS convention."""
        pass


class PCSParser(ABC):
    """Base interface object for the parser.

    It loads the pcs files into the generic pcs object. Once a parameter file is loaded,
    it can be exported to another file
    """

    def __init__(self: PCSParser, inherit: PCSParser = None) -> None:
        """Initialize the PCSParser."""
        if inherit is None:
            self.pcs = PCSObject()
        else:
            self.pcs = inherit.pcs

    @staticmethod
    def _format_string_to_enum(string: str) -> PCSConvention:
        """Convert string to PCSConvention."""
        for form in PCSConvention:
            if form.value == string.lower():
                return form
        raise Exception("ERROR: parameter configuration space format is not supported.")

    def check_validity(self: PCSParser) -> bool:
        """Check the validity of the pcs."""
        # TODO implement

        # check if for all parameters in constraints and forbidden clauses exists
        # Check for conflict between default values and constraints and forbidden clauses
        return True

    def load(self: PCSParser, filepath: Path, convention: str = "smac") -> None:
        """Main import function."""
        if isinstance(filepath, str):
            filepath = Path(filepath)
        convention = self._format_string_to_enum(convention)

        if convention == PCSConvention.SMAC:
            lines = filepath.open().readlines()
            parser = SMACParser(self)
            parser.parse(lines)
            self.pcs = parser.pcs
        elif convention == PCSConvention.ConfigSpace:
            if filepath.suffix == ".yaml":
                self.pcs = ConfigSpace.ConfigurationSpace.from_yaml(filepath)
            elif filepath.suffix == ".json":
                self.pcs = ConfigSpace.ConfigurationSpace.from_json(filepath)
            else:
                raise Exception(f"File type for {convention.value}: {filepath.suffix}"
                                "not in accepted types: {'.yaml', '.json'}")
        else:
            raise Exception(f"ERROR: Importing the pcs convention for {convention.value}"
                            " is not yet implemented.")

    def export(self: PCSParser,
               destination: Path,
               convention: str = "smac") -> None:
        """Main export function."""
        convention = self._format_string_to_enum(convention)
        # TODO: SMAC2 writer
        if convention == PCSConvention.ParamILS:
            pcs = ParamILSParser(self).compile()
            destination.open("w").write("### Parameter file generated by Sparkle\n"
                                        f"{pcs}\n")
        elif convention == PCSConvention.IRACE:
            pcs, forbidden = IRACEParser(self).compile()
            forbidden_file_name = destination.stem + "_forbidden.txt"
            (destination.parent / forbidden_file_name).open("w").write(forbidden)
            destination.open("w").write("### Parameter file generated by Sparkle\n"
                                        f"{pcs}\n")
        elif convention == PCSConvention.ConfigSpace:
            self.pcs.to_json(destination)
        else:
            raise Exception(f"ERROR: Exporting the pcs convention for {convention.value}"
                            " is not yet implemented.")

    def get_configspace(self: PCSObject) -> ConfigSpace.ConfigurationSpace:
        """Get the ConfigurationSpace representationof the PCS file."""
        cs = ConfigSpace.ConfigurationSpace()
        parameters = [p for p in self.pcs.params if p["type"] == "parameter"]
        constraints = [c for c in self.pcs.params if c["type"] == "constraint"]
        forbidden = [f for f in self.pcs.params if f["type"] == "forbidden"]
        for p in parameters:
            if p["structure"] == "integer":
                csparam = ConfigSpace.UniformIntegerHyperparameter(
                    name=p["name"],
                    lower=int(p["domain"][0]),
                    upper=int(p["domain"][1]),
                    default_value=int(p["default"]),
                    log=p["scale"] == "log",
                )
                # BetaIntegerHyperparameter
                # Requires a alpha and beta
                # NormalIntegerHyperparameter
                # Requires a mu and sigma (mean and std deviation)
            elif p["structure"] == "real":
                csparam = ConfigSpace.UniformFloatHyperparameter(
                    name=p["name"],
                    lower=float(p["domain"][0]),
                    upper=float(p["domain"][1]),
                    default_value=float(p["default"]),
                    log=p["scale"] == "log",
                )
                # BetaFloatHyperparameter
                # Requires an Alpha and Beta of the distribution
                # NormalFloatHyperparameter
                # Requires mu and sigma (Mean and std dev)
            elif p["structure"] == "categorical":
                csparam = ConfigSpace.CategoricalHyperparameter(
                    name=p["name"],
                    choices=p["domain"],
                    default_value=p["default"],
                    # Does not seem to contain any weights?
                )
            elif p["structure"] == "ordinal":
                csparam = ConfigSpace.OrdinalHyperparameter(
                    name=p["name"],
                    sequence=p["domain"],
                    default_value=p["default"],
                )
            else:
                raise Exception(f"ERROR: Unknown parameter structure: {p['structure']}")
            # NOTE: Missing:
            # elif p["structure"]  == "constant":
            cs.add(csparam)
        for constraint in constraints:
            # Constraints are called conditions in ConfigSpace, connected w conjections
            conjunction = None
            for operator, clause in constraint["conditions"]:
                parent = cs[clause["parameter"]]
                try:
                    if "items" in clause:
                        values = [type(parent.default_value)(i) for i in clause["items"]]
                    else:
                        values = type(parent.default_value)(clause["value"])
                except Exception:
                    raise TypeError(
                        f"The clause {clause['items']} contains values that are not of "
                        f"the same type as parameter {clause['parameter']} "
                        f"[{type(parent.default_value)}].")
                if "quantifier" not in clause:
                    condition = ConfigSpace.InCondition(
                        child=cs[constraint["parameter"]],
                        parent=parent,
                        values=values,
                    )
                elif clause["quantifier"] == "==":
                    condition = ConfigSpace.EqualsCondition(
                        child=cs[constraint["parameter"]],
                        parent=parent,
                        value=values,
                    )
                elif clause["quantifier"] == "!=":
                    condition = ConfigSpace.NotEqualsCondition(
                        child=cs[constraint["parameter"]],
                        parent=parent,
                        value=values,
                    )
                elif clause["quantifier"] == ">":
                    condition = ConfigSpace.GreaterThanCondition(
                        child=cs[constraint["parameter"]],
                        parent=parent,
                        value=values,
                    )
                elif clause["quantifier"] == "<":
                    condition = ConfigSpace.LessThanCondition(
                        child=cs[constraint["parameter"]],
                        parent=parent,
                        value=values,
                    )
                # NOTE from SMAC2:
                # There is no support for parenthesis with conditionals.
                # The && connective has higher precedence than ||, so
                # a||b&& c||d is the same as: a||(b&&c)||d
                if conjunction is None:
                    conjunction = condition
                elif operator == "&&":
                    conjunction = ConfigSpace.AndConjunction(conjunction, condition)
                elif operator == "||":
                    conjunction = ConfigSpace.OrConjunction(conjunction, condition)
                else:
                    raise Exception(f"ERROR: Unknown conjunction operator: {operator}")
            cs.add(conjunction)
        for forbid in forbidden:
            # TODO: This section is ill supported by PCSParser so the values
            # we find are wrong or incomplete for advanced clause types:
            # It does not support &&/|| operators or multi variable in a single statement
            if forbid["clause_type"] == "advanced":
                print("WARNING: Advanced clauses not supported in PCSParser. "
                      f"Skipping forbidden clause: {forbid['clauses']}")
                continue
            # Therefore, we can only add forbidden with "=" operator and "&&" conjunction
            conjunction = None

            for clause in forbid["clauses"]:
                parameter = cs[clause["param"]]
                clause = ConfigSpace.ForbiddenEqualsClause(
                    hyperparameter=parameter,
                    value=type(parameter.default_value)(clause["value"]),
                )
                if conjunction is None:
                    conjunction = clause
                else:
                    conjunction = ConfigSpace.ForbiddenAndConjunction(conjunction,
                                                                      clause)
            cs.add(conjunction)
        return cs


class SMACParser(PCSParser):
    """The SMAC parser class."""

    def parse(self: SMACParser, lines: list[str]) -> None:
        """Parse the pcs file."""
        self.pcs.clear()

        # PARAMS
        for line in lines:
            # The only forbidden characters in parameter names are:
            # spaces, commas, quotes, and parentheses
            regex = (r"(?P<name>[^\s\"',]*)\s+(?P<structure>\w*)\s+(?P<domain>(\[|\{)"
                     r".*(\]|\}))\s*\[(?P<default>.*)\]\s*(?P<scale>log)"
                     r"*\s*#*(?P<comment>.*)")
            m = re.match(regex, line)
            if m is not None:
                fields = m.groupdict()
                fields["domain"] = re.sub(r"(?:\[|\]|\{|\})", "", fields["domain"])
                fields["domain"] = re.split(r"\s*,\s*", fields["domain"])
                self.pcs.add_param(**fields)
                continue

            # CONDITIONS
            regex = (r"(?P<parameter>[^\s\"',]+)\s*\|\s"
                     r"*(?P<conditions>.+)\s*#*(?P<comment>.*)")
            m = re.match(regex, line)
            if m is not None:
                constraint = m.groupdict()
                constraint["conditions"] = self._parse_conditions(
                    constraint["conditions"])
                self.pcs.add_constraint(**constraint)
                continue

            # FORBIDDEN CLAUSES
            regex = r"\s*\{(?P<clauses>[^\}]+)\}\s*#*(?P<comment>.*)"
            m = re.match(regex, line)
            if m is not None:
                forbidden = m.groupdict()
                conditions = []
                # Simple clauses
                # {<parameter name 1>=<value 1>, ..., <parameter name N>=<value N>}
                if "," in forbidden["clauses"]:
                    forbidden["clause_type"] = "simple"
                    for clause in re.split(r"\s*,\s*", forbidden["clauses"]):
                        m = re.match(r"(?P<param>[^\s\"',=]+)\s*=\s*"
                                     r"(?P<value>[^\s\"',]+)", clause)
                        if m is not None:
                            conditions.append(m.groupdict())
                        else:
                            print(clause, "ERROR")

                else:  # Advanced clauses
                    forbidden["clause_type"] = "advanced"
                    # TODO decide if we need to further parse this down
                    conditions = [expr for expr in re.split(r"\s*(?:\|\||&&)\s*",
                                                            forbidden["clauses"])]

                if len(conditions) == 0:
                    raise Exception(f"ERROR: cannot parse the following line:\n'{line}'")

                forbidden["clauses"] = conditions

                self.pcs.add_forbidden(**forbidden)
                continue

            # COMMENTLINE
            regex = r"\s*#(?P<comment>.*)"
            m = re.match(regex, line)
            if m is not None:
                comment = m.groupdict()
                self.pcs.add_comment(**comment)
                continue

            # EMTPY LINE
            regex = r"^\s*$"
            m = re.match(regex, line)
            if m is not None:
                continue

            # RAISE ERROR
            raise Exception(f"ERROR: cannot parse the following line: \n'{line}'")

        return

    def _parse_conditions(self: SMACParser, conditions: str) -> list[tuple]:
        """Parse the conditions."""
        conditionlist = []
        condition = None
        operator = None
        nested = 0
        nested_start = 0
        condition_start = 0
        for pos, char in enumerate(conditions):
            # Nested clauses
            if char == "(":
                if nested == 0:
                    nested_start = pos
                nested += 1
            elif char == ")":
                nested -= 1
                if nested == 0:
                    condition = self._parse_conditions(conditions[nested_start + 1:pos])
                    conditionlist.append((operator, condition))
                    if (pos + 1) == len(conditions):
                        return conditionlist

            if pos > 1 and nested == 0:
                for op in ["||", "&&"]:
                    if conditions[pos - 1: pos + 1] == op:
                        if not isinstance(condition, list):
                            condition = self._parse_condition(
                                conditions[condition_start:pos - 1])
                            conditionlist.append((operator, condition))

                        operator = op
                        condition_start = pos + 1

        condition = self._parse_condition(conditions[condition_start:len(conditions)])
        conditionlist.append((operator, condition))

        return conditionlist

    @staticmethod
    def _parse_condition(condition: str) -> dict:
        """Parse the condition."""
        cont = False

        m = re.match(r"\s*(?P<parameter>[^\s\"',]+)\s*(?P<quantifier>==|!=|<|>|<=|>=)"
                     r"\s*(?P<value>[^\s\"',]+)\s*", condition)
        if m is not None:
            condition = {
                **m.groupdict(),
                "type": "numerical",
            }
            cont = True

        if not cont:
            m = re.match(r"\s*(?P<parameter>[^\s\"',]+)\s+"
                         r"in\s*\{(?P<items>[^\}]+)\}\s*", condition)
            if m is not None:
                condition = {
                    **m.groupdict(),
                    "type": "categorical",
                }
                condition["items"] = re.split(r",\s*", condition["items"])
            cont = True

        if not cont:
            raise Exception(f"ERROR: Couldn't parse '{condition}'")

        return condition

    def compile(self: SMACParser) -> str:
        """Compile the PCS."""
        # TODO implement
        pass


class ParamILSParser(PCSParser):
    """PCS parser for ParamILS format."""

    def parse(self: ParamILSParser, lines: list[str]) -> None:
        """Parse the PCS."""
        # TODO implement
        pass

    def compile(self: ParamILSParser) -> str:
        """Compile the PCS."""
        # TODO Produce warning if certain specifications cannot be kept in this format
        # TODO granularity parameter that sets how log and real ranges should be expanded
        granularity = 20

        lines = []
        for item in self.pcs.params:
            if item["type"] == "parameter":
                if item["structure"] in ["ordinal", "categorical"]:
                    domain = ",".join(item["domain"])
                elif item["structure"] == "integer":
                    if len(item["domain"]) != 2:
                        raise ValueError(f"Domain {item['domain']} not supported.")
                    item["default"] = int(item["default"])
                    (minval, maxval) = [int(i) for i in item["domain"]]
                    if item["scale"] != "log":
                        # domain = f"{minval}, {(minval + 1)}..{maxval}"
                        domain = list(np.linspace(minval, maxval, granularity))
                        domain = list(set(np.round(domain).astype(int)))  # Cast to int
                        if item["default"] not in domain:
                            domain += [item["default"]]
                        domain.sort()

                        domain = ",".join([str(i) for i in domain])
                    else:
                        domain = list(np.unique(np.geomspace(minval, maxval, granularity,
                                                             dtype=int)))
                        # add default value
                        if item["default"] not in domain:
                            domain += [item["default"]]
                            domain.sort()

                        domain = ",".join([str(i) for i in domain])

                elif item["structure"] == "real":
                    if len(item["domain"]) != 2:
                        raise ValueError(f"Domain {item['domain']} not supported.")

                    (minval, maxval) = [float(i) for i in item["domain"]]
                    item["default"] = float(item["default"])
                    if item["scale"] != "log":
                        domain = list(np.linspace(minval, maxval, granularity))
                    else:
                        domain = list(np.unique(np.geomspace(minval, maxval, granularity,
                                                             dtype=float)))
                    # add default value
                    if item["default"] not in domain:
                        domain += [item["default"]]
                        domain.sort()

                    # Filter duplicated in string format
                    domain = list(set([f"{i}" for i in domain]))
                    domain.sort(key=float)
                    domain = ",".join(domain)

                domain = "{" + domain + "}"
                line = f"{item['name']} {domain} [{item['default']}]"
                if item["comment"] != "":
                    line += f" #{item['comment']}"

                lines.append(line)

        lines.append("")

        for item in self.pcs.params:
            if item["type"] == "constraint":
                line = f"{item['parameter']} | "
                line += self._compile_conditions(item["conditions"])
                if item["comment"] != "":
                    line += f" #{item['comment']}"
                lines.append(line)

        lines.append("")

        for item in self.pcs.params:
            if item["type"] == "forbidden":
                if item["clause_type"] == "simple":
                    clauses = [f"{cls['param']}={cls['value']}"
                               for cls in item["clauses"]]
                    line = "{" + ",".join(clauses) + "}"
                    if item["comment"] != "":
                        line += f"#{item['comment']}"
                    lines.append(line)
                else:
                    print("WARNING: Advanced forbidden clauses "
                          "are not supported by ParamILS.")
                pass

        lines = "\n".join(lines)
        return lines

    def _compile_conditions(self: ParamILSParser, conditions: list[tuple]) -> str:
        """Compile a list of conditions."""
        line = ""
        for operator, condition in conditions:
            if operator is not None:
                line += f" {operator} "

            if isinstance(condition, list):
                line += f"({self._compile_conditions(condition)})"
            else:
                if condition["type"] == "numerical":
                    line += f"{condition['parameter']} in " + "{"
                    param = self.pcs.get(condition["parameter"])
                    if param["structure"] == "categorical":
                        if condition["value"] in param["domain"]:
                            line += f"{condition['value']}" + "}"
                    # line += "{parameter} {quantifier} {value}".format(**condition)
                if condition["type"] == "categorical":
                    items = ", ".join(condition["items"])
                    line += f"{condition['parameter']} in {{{items}}}"
        return line


class IRACEParser(PCSParser):
    """Base interface object for the parser.

    It loads the IRACE pcs files into the generic pcs object.
    Once a parameter file is loaded, it can be exported to another file.
    """

    def __init__(self: IRACEParser, inherit: IRACEParser = None) -> None:
        """Initialize the IRACEParser."""
        if inherit is None:
            self.pcs = PCSObject()
        else:
            self.pcs = inherit.pcs

    def parse(self: IRACEParser, lines: list[str]) -> None:
        """Parse the pcs file."""
        # TODO implement
        pass

    def compile(self: IRACEParser) -> tuple[str, str]:
        """Compile the PCS."""
        # Create pcs table
        header = ["# name", "switch", "type", "values",
                  "[conditions (using R syntax)]"]
        rows = []
        forbidden = [f for f in self.pcs.params if f["type"] == "forbidden"]
        constraints = [c for c in self.pcs.params if c["type"] == "constraint"]
        for param in [p for p in self.pcs.params if p["type"] == "parameter"]:
            # IRACE writes conditions on the same line as param definitions
            param_constraint = [c for c in constraints
                                if c["parameter"] == param["name"]]
            condition_str = "|"
            for constraint in param_constraint:
                for operator, condition in constraint["conditions"]:
                    operator = operator if operator is not None else ""
                    condition_str +=\
                        (f" {operator} {condition['parameter']} %in% "
                            f"{condition['type'][0]}({','.join(condition['items'])})")
            if condition_str == "|":
                condition_str = ""
            rows.append([param["name"],  # Parameter name
                         f'"--{param["""name"""]} "',  # Parameter argument name
                         param["structure"][0],  # Parameter type
                         f"({','.join(param['domain'])})",  # Parameter range/domain
                         condition_str])  # Parameter conditions
        forbidden_rows = []
        for f in forbidden:
            forbidden_rows.append(" & ".join([f"({c['param']} = {c['value']})"
                                              for c in f["clauses"]]))
        return tabulate.tabulate(rows, headers=header, tablefmt="plain",
                                 numalign="left"), "\n".join(forbidden_rows)
