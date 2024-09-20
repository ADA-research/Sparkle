"""The Parameter Configuration Space Parser class."""
from __future__ import annotations
import re
import sys
import numpy as np
from enum import Enum
from abc import ABC
from pathlib import Path


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


class PCSConvention(Enum):
    """Internal pcs convention enum."""
    unknown = ""
    SMAC = "smac"
    ParamILS = "paramils"


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
            if form.value == string:
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

        # TODO check if file actually exists
        lines = filepath.open().readlines()
        if convention == PCSConvention.SMAC:
            parser = SMACParser(self)
            parser.parse(lines)
            self.pcs = parser.pcs
        else:
            raise Exception(f"ERROR: Importing the pcs convention for {convention.value}"
                            " is not yet implemented.")

    def export(self: PCSParser,
               convention: str = "smac",
               destination: Path = None) -> None:
        """Main export function."""
        convention = self._format_string_to_enum(convention)
        if convention == PCSConvention.ParamILS:
            pcs = ParamILSParser(self).compile()
        else:
            raise Exception(f"ERROR: Exporting the pcs convention for {convention.value}"
                            " is not yet implemented.")
        destination.open("w").write(pcs)


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

            # CONSTRAINTS
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

                    (minval, maxval) = [int(i) for i in item["domain"]]
                    if item["scale"] != "log":
                        # domain = f"{minval}, {(minval + 1)}..{maxval}"
                        domain = list(np.linspace(minval, maxval, granularity))
                        domain = list(set(np.round(domain).astype(int)))  # Cast to int
                        if int(item["default"]) not in domain:
                            domain += [int(item["default"])]
                        domain.sort()

                        domain = ",".join([str(i) for i in domain])
                    else:
                        domain = list(np.unique(np.geomspace(minval, maxval, granularity,
                                                             dtype=int)))
                        # add default value
                        if int(item["default"]) not in domain:
                            domain += [int(item["default"])]
                            domain.sort()

                        domain = ",".join([str(i) for i in domain])

                elif item["structure"] == "real":
                    if len(item["domain"]) != 2:
                        raise ValueError(f"Domain {item['domain']} not supported.")

                    (minval, maxval) = [float(i) for i in item["domain"]]
                    if item["scale"] != "log":
                        domain = list(np.linspace(minval, maxval, granularity))
                    else:
                        domain = list(np.unique(np.geomspace(minval, maxval, granularity,
                                                             dtype=float)))
                    # add default value
                    if float(item["default"]) not in domain:
                        domain += [float(item["default"])]
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

        for item in self.pcs.params:
            if item["type"] == "constraint":
                line = f"{item['parameter']} | "
                line += self._compile_conditions(item["conditions"])
                if item["comment"] != "":
                    line += f" #{item['comment']}"
                lines.append(line)

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
