"""Methods to deal with Parameter Configuration Space files."""
from pathlib import Path
from sparkle.solver import Solver


def write_configuration_pcs(solver: Solver, config_str: str, tmp_path: Path) -> None:
    """Write configuration to a new PCS file.

    Args:
        solver: Solver object
        config_str: Configuration to write
        tmp_path: Path to place the latest configuration pcs
    """
    # Read optimised configuration and convert to dict
    optimised_configuration_list = config_str.split()

    # Create dictionary
    config_dict = {}
    for i in range(0, len(optimised_configuration_list), 2):
        # Remove dashes and spaces from parameter names, and remove quotes and
        # spaces from parameter values before adding them to the dict
        config_dict[optimised_configuration_list[i].strip(" -")] = (
            optimised_configuration_list[i + 1].strip(" '"))

    # Read existing PCS file and create output content
    pcs_file = solver.get_pcs_file()
    pcs_file_out = []

    with pcs_file.open("r") as infile:
        for line in infile:
            # Copy empty lines
            if not line.strip():
                line_out = line
            # Don't mess with conditional (containing '|') and forbidden (starting
            # with '{') parameter clauses, copy them as is
            elif "|" in line or line.startswith("{"):
                line_out = line
            # Also copy parameters that do not appear in the optimised list
            # (if the first word in the line does not match one of the parameter names
            # in the dict)
            elif line.split()[0] not in config_dict:
                line_out = line
            # Modify default values with optimised values
            else:
                words = line.split("[")
                if len(words) == 2:
                    # Second element is default value + possible tail
                    param_name = line.split()[0]
                    param_val = config_dict[param_name]
                    tail = words[1].split("]")[1]
                    line_out = words[0] + "[" + param_val + "]" + tail
                elif len(words) == 3:
                    # Third element is default value + possible tail
                    param_name = line.split()[0]
                    param_val = config_dict[param_name]
                    tail = words[2].split("]")[1]
                    line_out = words[0] + words[1] + "[" + param_val + "]" + tail
                else:
                    # This does not seem to be a line with a parameter definition, copy
                    # as is
                    line_out = line
            pcs_file_out.append(line_out)

    latest_configuration_pcs_path = tmp_path / "latest_configuration.pcs"

    with latest_configuration_pcs_path.open("w") as outfile:
        for element in pcs_file_out:
            outfile.write(str(element))
