"""Parameter Configuration Space tools."""
from __future__ import annotations
import re
import ast
from enum import Enum
from pathlib import Path

import ConfigSpace.conditions
import tabulate
import ConfigSpace
from ConfigSpace import ConfigurationSpace
from sparkle.tools.configspace import expression_to_configspace


class PCSConvention(Enum):
    """Internal pcs convention enum."""
    UNKNOWN = "UNKNOWN"
    SMAC = "smac"
    ParamILS = "paramils"
    IRACE = "irace"
    ConfigSpace = "configspace"


class PCSConverter:
    """Parser class independent file of notation."""
    section_regex = re.compile(r"\[(?P<name>[a-zA-Z]+?)\]\s*(?P<comment>#.*)?$")
    illegal_param_name = re.compile(r"[!:\-+@!#$%^&*()=<>?/\|~` ]")

    smac2_params_regex = re.compile(r"^(?P<name>[a-zA-Z0-9_]+)\s+(?P<type>[a-zA-Z]+)\s+"
                                    r"(?P<values>[a-zA-Z0-9\-\[\]{}_,. ]+)\s*"
                                    r"\[(?P<default>[a-zA-Z0-9._-]+)\]?\s*"
                                    r"(?P<scale>log)?\s*(?P<comment>#.*)?$")
    smac2_conditions_regex = re.compile(r"^(?P<parameter>[a-zA-Z0-9_]+)\s*\|\s*"
                                        r"(?P<expression>.+)$")
    smac2_forbidden_regex = re.compile(r"\{(?P<forbidden>.+)\}$")

    paramils_params_regex = re.compile(
        r"^(?P<name>[a-zA-Z0-9@!#:_-]+)\s*"
        r"(?P<values>{[a-zA-Z0-9._+\-\, ]+})\s*"
        r"\[(?P<default>[a-zA-Z0-9._\-+ ]+)\]?\s*"
        r"(?P<comment>#.*)?$")
    paramils_conditions_regex = re.compile(r"^(?P<parameter>[a-zA-Z0-9@!#:_-]+)\s*\|\s*"
                                           r"(?P<expression>.+)$")

    irace_params_regex = re.compile(
        r"^(?P<name>[a-zA-Z0-9_]+)\s+"
        r"(?P<switch>[\"a-zA-Z0-9_\- ]+)\s+"
        r"(?P<type>[cior])(?:,)?(?P<scale>log)?\s+"
        r"(?P<values>[a-zA-Z0-9\-()_,. ]+)\s*"
        r"(?:\|)?(?P<conditions>[a-zA-Z-0-9_!=<>\%()\&\|\. ]*)?\s*"
        r"(?P<comment>#.*)?$")

    @staticmethod
    def get_convention(file: Path) -> PCSConvention:
        """Determines the format of a pcs file."""
        try:
            ConfigSpace.ConfigurationSpace.from_yaml(file)
            return PCSConvention.ConfigSpace
        except Exception:
            pass
        try:
            ConfigSpace.ConfigurationSpace.from_json(file)
            return PCSConvention.ConfigSpace
        except Exception:
            pass

        file_contents = file.open().readlines()
        for line in file_contents:
            if line.startswith("#"):  # Comment line
                continue
            if "#" in line:
                line, _ = line.split("#", maxsplit=1)
            line = line.strip()
            if re.match(PCSConverter.smac2_params_regex, line):
                return PCSConvention.SMAC
            elif re.match(PCSConverter.paramils_params_regex, line):
                return PCSConvention.ParamILS
            elif re.match(PCSConverter.irace_params_regex, line):
                return PCSConvention.IRACE
        return PCSConvention.UNKNOWN

    @staticmethod
    def parse(file: Path, convention: PCSConvention = None) -> ConfigurationSpace:
        """Determines the format of a pcs file and parses into Configuration Space."""
        if not convention:
            convention = PCSConverter.get_convention(file)
        if convention == PCSConvention.ConfigSpace:
            if file.suffix == ".yaml":
                return ConfigSpace.ConfigurationSpace.from_yaml(file)
            if file.suffix == ".json":
                return ConfigSpace.ConfigurationSpace.from_json(file)
        if convention == PCSConvention.SMAC:
            return PCSConverter.parse_smac(file)
        if convention == PCSConvention.ParamILS:
            return PCSConverter.parse_paramils(file)
        if convention == PCSConvention.IRACE:
            return PCSConverter.parse_irace(file)
        raise Exception(
            f"PCS convention not recognised based on any lines in file:\n{file}")

    @staticmethod
    def parse_smac(content: list[str] | Path) -> ConfigurationSpace:
        """Parses a SMAC2 file."""
        space_name = content.name if isinstance(content, Path) else None
        content = content.open().readlines() if isinstance(content, Path) else content
        cs = ConfigurationSpace(space_name)
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
                        upper=int(values[-1]),
                        default_value=int(default),
                        log=scale == "log",
                        meta=comment,
                    )
                elif parameter_type == "real":
                    values = ast.literal_eval(values)
                    csparam = ConfigSpace.UniformFloatHyperparameter(
                        name=name,
                        lower=float(values[0]),
                        upper=float(values[-1]),
                        default_value=float(default),
                        log=scale == "log",
                        meta=comment,
                    )
                elif parameter_type == "categorical":
                    values = re.sub(r"[{}\s]+", "", values).split(",")
                    csparam = ConfigSpace.CategoricalHyperparameter(
                        name=name,
                        choices=values,
                        default_value=default,
                        meta=comment,
                        # Does not seem to contain any weights?
                    )
                elif parameter_type == "ordinal":
                    values = re.sub(r"[{}\s]+", "", values).split(",")
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
                condition = re.sub(r"(?<![<>!=])=(?<![=])", "==", condition)
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
                # NOTE: According to MA & JR, these were never actually supported
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
                forbidden = re.sub(r"(?<![<>!=])=(?![=])", "==", forbidden)
                forbidden = expression_to_configspace(forbidden, cs)
                cs.add(forbidden)
            else:
                raise Exception(
                    f"SMAC2 PCS expression not recognised on line:\n{line}")
        return cs

    @staticmethod
    def parse_paramils(content: list[str] | Path) -> ConfigurationSpace:
        """Parses a paramils file."""
        space_name = content.name if isinstance(content, Path) else None
        content = content.open().readlines() if isinstance(content, Path) else content
        cs = ConfigurationSpace(name=space_name)
        conditions_lines = {}
        for line in content:
            line = line.strip()
            if not line or line.startswith("#"):  # Empty or comment
                continue
            comment = None
            if re.match(PCSConverter.paramils_params_regex, line):
                parameter = re.fullmatch(PCSConverter.paramils_params_regex, line)
                name = parameter.group("name")
                if re.match(PCSConverter.illegal_param_name, name):
                    # ParamILS is flexible to which parameters are allowed.
                    # We do not allow it as it creates many problems with parsing
                    # expressions
                    raise ValueError(
                        f"ParamILS parameter name not allowed: {name}. "
                        "This is supported by ParamILS, but not by PCSConverter.")
                values = parameter.group("values")
                values = values.replace("..", ",")  # Replace automatic expansion
                try:
                    values = list(ast.literal_eval(values))  # Values are sets
                    values = sorted(values)
                    if any([isinstance(v, float) for v in values]):
                        parameter_type = float
                    else:
                        parameter_type = int
                except Exception:  # of strings (Categorical)
                    values = values.replace("{", "").replace("}", "").split(",")
                    parameter_type = str
                if len(values) == 1:  # Not allowed by ConfigSpace for int / float
                    values = [str(values[0])]
                    parameter_type = str
                default = parameter.group("default")
                comment = parameter.group("comment")
                if parameter_type == int:
                    csparam = ConfigSpace.UniformIntegerHyperparameter(
                        name=name,
                        lower=int(values[0]),
                        upper=int(values[-1]),
                        default_value=int(default),
                        meta=comment,
                    )
                elif parameter_type == float:
                    csparam = ConfigSpace.UniformFloatHyperparameter(
                        name=name,
                        lower=float(values[0]),
                        upper=float(values[-1]),
                        default_value=float(default),
                        meta=comment,
                    )
                elif parameter_type == str:
                    csparam = ConfigSpace.CategoricalHyperparameter(
                        name=name,
                        choices=values,
                        default_value=default,
                        meta=comment,
                    )
                cs.add(csparam)
            elif re.match(PCSConverter.paramils_conditions_regex, line):
                # Break up the expression into the smallest possible pieces
                match = re.fullmatch(PCSConverter.paramils_conditions_regex, line)
                parameter, condition =\
                    match.group("parameter").strip(), match.group("expression")
                condition = condition.replace(" || ", " or ").replace(" && ", " and ")
                condition = re.sub(r"(?<![<>!=])=(?<![=])", "==", condition)
                condition = re.sub(r"!==", "!=", condition)
                # ParamILS supports multiple lines of conditions for a single parameter
                # so we collect, with the AND operator and parse + add them later
                if parameter not in conditions_lines:
                    conditions_lines[parameter] = condition
                else:
                    conditions_lines[parameter] += " and " + condition
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
                # NOTE: According to MA & JR, these were never actually supported
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
                forbidden = re.sub(r"(?<![<>!=])=(?![=])", "==", forbidden)
                forbidden = expression_to_configspace(forbidden, cs)
                cs.add(forbidden)
            else:
                raise Exception(
                    f"ParamILS PCS expression not recognised on line: {line}")
        # Add the condition
        for pname, cond in conditions_lines.items():  # Add conditions
            condition = expression_to_configspace(cond, cs,
                                                  target_parameter=cs[pname])
            cs.add(condition)
        return cs

    @staticmethod
    def parse_irace(content: list[str] | Path) -> ConfigurationSpace:
        """Parses a irace file."""
        space_name = content.name if isinstance(content, Path) else None
        content = content.open().readlines() if isinstance(content, Path) else content
        cs = ConfigurationSpace(name=space_name)
        standardised_conditions = []
        forbidden_flag, global_flag = False, False
        for line in content:
            line = line.strip()
            if not line or line.startswith("#"):  # Empty or comment
                continue
            if re.match(PCSConverter.section_regex, line):
                section = re.fullmatch(PCSConverter.section_regex, line)
                if section.group("name") == "forbidden":
                    forbidden_flag, global_flag = True, False
                    continue
                elif section.group("name") == "global":
                    global_flag, forbidden_flag = True, False
                    continue
                else:
                    raise Exception(
                        f"IRACE PCS section not recognised on line:\n{line}")
            elif global_flag:  # Parse global statements
                continue  # We do not parse global group
            elif forbidden_flag:  # Parse forbidden statements
                # Parse the forbidden statement to standardised format
                forbidden_expr = re.sub(r" \& ", " and ", line)
                forbidden_expr = re.sub(r" \| ", " or ", forbidden_expr)
                forbidden_expr = re.sub(r" \%in\% ", " in ", forbidden_expr)
                forbidden_expr = re.sub(r" [co]\(", " (", forbidden_expr)
                forbidden_expr = expression_to_configspace(forbidden_expr, cs)
                cs.add(forbidden_expr)
            elif re.match(PCSConverter.irace_params_regex, line):
                parameter = re.fullmatch(PCSConverter.irace_params_regex, line)
                name = parameter.group("name")
                parameter_type = parameter.group("type")
                # NOTE: IRACE supports depedent parameter domains, e.g. parameters which
                # domain relies on another parameter: p2 "--p2" r ("p1", "p1 + 10")"
                # and is limited to the operators: +,-, *, /, %%, min, max
                values = ast.literal_eval(parameter.group("values"))
                scale = parameter.group("scale")
                conditions = parameter.group("conditions")
                comment = parameter.group("comment")
                # Convert categorical / ordinal values to strings
                if parameter_type == "c" or parameter_type == "o":
                    values = [str(i) for i in values]
                else:
                    if any(operator in values
                           for operator in ["+", "-", "*", "/", "%", "min", "max"]):
                        raise ValueError("Dependent parameter domains not supported by "
                                         "ConfigurationSpace.")
                    lower_bound, upper_bound = values[0], values[1]
                if parameter_type == "c":
                    csparam = ConfigSpace.CategoricalHyperparameter(
                        name=name,
                        choices=values,
                        meta=comment,
                    )
                elif parameter_type == "o":
                    csparam = ConfigSpace.OrdinalHyperparameter(
                        name=name,
                        sequence=values,
                        meta=comment,
                    )
                elif parameter_type == "r":
                    csparam = ConfigSpace.UniformFloatHyperparameter(
                        name=name,
                        lower=float(lower_bound),
                        upper=float(upper_bound),
                        log=scale == "log",
                        meta=comment,
                    )
                elif parameter_type == "i":
                    csparam = ConfigSpace.UniformIntegerHyperparameter(
                        name=name,
                        lower=int(lower_bound),
                        upper=int(upper_bound),
                        log=scale == "log",
                        meta=comment,
                    )
                cs.add(csparam)
                if conditions:
                    # Convert the expression to standardised format
                    conditions = re.sub(r" \& ", " and ", conditions)
                    conditions = re.sub(r" \| ", " or ", conditions)
                    conditions = re.sub(r" \%in\% ", " in ", conditions)
                    conditions = re.sub(r" [cior]\(", " (", conditions)
                    conditions = conditions.strip()
                    standardised_conditions.append((csparam, conditions))
            else:
                raise Exception(
                    f"IRACE PCS expression not recognised on line:\n{line}")

        # We can only add the conditions after all parameters have been parsed:
        for csparam, conditions in standardised_conditions:
            conditions = expression_to_configspace(conditions, cs,
                                                   target_parameter=csparam)
            cs.add(conditions)
        return cs

    @staticmethod
    def export(configspace: ConfigurationSpace,
               pcs_format: PCSConvention, file: Path) -> str | None:
        """Exports a config space object to a specific PCS convention.

        Args:
            configspace: ConfigurationSpace, the space to convert
            pcs_format: PCSConvention, the convention to conver to
            file: Path, the file to write to. If None, will return string.

        Returns:
            String in case of no file path given, otherwise None.
        """
        # Create pcs table
        declaration = f"### {pcs_format.name} Parameter Configuration Space file "\
                      "generated by Sparkle\n"
        rows = []
        extra_rows = []
        if pcs_format == PCSConvention.SMAC or pcs_format == PCSConvention.ParamILS:
            import numpy as np
            granularity = 20  # For ParamILS. TODO: Make it parametrisable
            header = ["# Parameter Name", "type", "values",
                      "default value", "scale", "comments"]
            parameter_map = {
                ConfigSpace.UniformFloatHyperparameter: "real",
                ConfigSpace.UniformIntegerHyperparameter: "integer",
                ConfigSpace.CategoricalHyperparameter: "categorical",
                ConfigSpace.OrdinalHyperparameter: "ordinal",
            }
            for parameter in list(configspace.values()):
                log = False
                if isinstance(parameter,
                              ConfigSpace.hyperparameters.NumericalHyperparameter):
                    log = parameter.log
                    if pcs_format == PCSConvention.ParamILS:  # Discretise
                        dtype = float if isinstance(
                            parameter, ConfigSpace.UniformFloatHyperparameter) else int
                        if log:
                            lower = 1e-5 if parameter.lower == 0 else parameter.lower
                            domain = list(np.unique(np.geomspace(
                                lower, parameter.upper, granularity,
                                dtype=dtype)))
                        else:
                            domain = list(np.linspace(parameter.lower, parameter.upper,
                                                      granularity, dtype=dtype))
                        if dtype(parameter.default_value) not in domain:  # Add default
                            domain += [dtype(parameter.default_value)]
                        domain = list(set(domain))  # Ensure unique values only
                        domain.sort()
                        domain = "{" + ",".join([str(i) for i in domain]) + "}"
                    else:  # SMAC2 takes ranges
                        domain = f"[{parameter.lower}, {parameter.upper}]"
                else:
                    domain = "{" + ",".join(parameter.choices) + "}"
                rows.append([parameter.name,
                             parameter_map[type(parameter)]
                             if not pcs_format == PCSConvention.ParamILS else "",
                             domain,
                             f"[{parameter.default_value}]",
                             "log"
                             if log and not pcs_format == PCSConvention.ParamILS else "",
                             f"# {parameter.meta}"])
            if configspace.conditions:
                extra_rows.extend(["", "# Parameter Conditions"])
                for condition in configspace.conditions:
                    condition_str = str(condition)
                    condition_str = condition_str.replace(
                        "(", "").replace(")", "")  # Brackets not allowed
                    condition_str = condition_str.replace("'", "")  # No quotes needed
                    condition_str = condition_str.replace(
                        f"{condition.child.name} | ", "").strip()
                    condition_str = f"{condition.child.name} | " + condition_str
                    if (pcs_format == PCSConvention.ParamILS
                            and re.search(r"[<>!=]+|[<>]=|[!=]=", condition_str)):
                        # TODO: Translate condition ParamILS expression (in)
                        continue
                    extra_rows.append(condition_str)
            if configspace.forbidden_clauses:
                extra_rows.extend(["", "# Forbidden Expressions"])
                for forbidden in configspace.forbidden_clauses:
                    forbidden_str = str(forbidden).replace("Forbidden: ", "")
                    forbidden_str = forbidden_str.replace("(", "{").replace(")", "}")
                    forbidden_str = forbidden_str.replace("'", "")
                    if (pcs_format == PCSConvention.ParamILS
                            and re.search(r"[<>!=]+|[<>]=|[!=]=", forbidden_str)):
                        # TODO: Translate condition ParamILS expression (in)
                        continue
                    extra_rows.append(forbidden_str)
        elif pcs_format == PCSConvention.IRACE:
            digits = 4  # Number of digits after decimal point required
            parameter_map = {
                ConfigSpace.UniformFloatHyperparameter: "r",
                ConfigSpace.UniformIntegerHyperparameter: "i",
                ConfigSpace.CategoricalHyperparameter: "c",
                ConfigSpace.OrdinalHyperparameter: "o",
            }
            header = ["# Parameter Name", "switch", "type", "values",
                      "[conditions (using R syntax)]", "comments"]
            for parameter in list(configspace.values()):
                parameter_conditions = []
                for c in configspace.conditions:
                    if c.child == parameter:
                        parameter_conditions.append(c)
                parameter_type = parameter_map[type(parameter)]
                condition_type = parameter_type if type(
                    parameter) == ConfigSpace.CategoricalHyperparameter else ""
                condition_str = " || ".join([str(c) for c in parameter_conditions])
                condition_str = condition_str.replace(f"{parameter.name} | ", "")
                condition_str = condition_str.replace(" in ", f" %in% {condition_type}")
                condition_str = condition_str.replace("{", "(").replace("}", ")")
                condition_str = condition_str.replace("'", "")  # No quotes around string
                condition_str = condition_str.replace(
                    " && ", " & ").replace(" || ", " | ")
                if isinstance(parameter,
                              ConfigSpace.hyperparameters.NumericalHyperparameter):
                    if parameter.log:
                        parameter_type += ",log"
                    domain = f"({parameter.lower}, {parameter.upper})"
                    if isinstance(parameter,
                                  ConfigSpace.hyperparameters.FloatHyperparameter):
                        # Format the floats to interpret the number of digits
                        # (Includes scientific notation)
                        lower, upper = (format(parameter.lower, ".16f").strip("0"),
                                        format(parameter.upper, ".16f").strip("0"))
                        param_digits = max(len(str(lower).split(".")[1]),
                                           len(str(upper).split(".")[1]))
                        # Check if we need to update the global digits
                        if param_digits > digits:
                            digits = param_digits
                else:
                    domain = "(" + ",".join(parameter.choices) + ")"
                rows.append([parameter.name,
                             f'"--{parameter.name} "',
                             parameter_type,
                             domain,  # Parameter range/domain
                             f"| {condition_str}" if condition_str else "",
                             f"# {parameter.meta}" if parameter.meta else ""])
            if configspace.forbidden_clauses:
                extra_rows.extend(["", "[forbidden]"])
                for forbidden_expression in configspace.forbidden_clauses:
                    forbidden_str = str(forbidden_expression).replace("Forbidden: ", "")
                    if " in " in forbidden_str:
                        type_char = parameter_map[
                            type(forbidden_expression.hyperparameter)]
                        forbidden_str.replace(" in ", f" %in% {type_char}")
                    forbidden_str = forbidden_str.replace(
                        " && ", " & ").replace(" || ", " | ")
                    extra_rows.append(forbidden_str)
            if digits > 4:  # Default digits is 4
                extra_rows.extend(["", "[global]", f"digits={digits}"])

        output = declaration + tabulate.tabulate(
            rows, headers=header,
            tablefmt="plain", numalign="left") + "\n"
        if extra_rows:
            output += "\n".join(extra_rows) + "\n"
        if file is None:
            return output
        file.open("w+").write(output)

    @staticmethod
    def validate(file_path: Path) -> bool:
        """Validate a pcs file."""
        # TODO: Determine which format
        # TODO: Verify each line, and the order in which they were written
        return
