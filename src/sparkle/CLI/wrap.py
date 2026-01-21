"""Command to wrap users' Solvers / Feature extractors for Sparkle."""

import sys
import subprocess
import re
import argparse
from pathlib import Path


from sparkle.solver import Solver
from sparkle.selector.extractor import Extractor
from sparkle.platform import Settings

from sparkle.CLI.help import logging as sl
from sparkle.CLI.help import argparse_custom as ac
from sparkle.CLI.help import global_variables as gv

import ConfigSpace
import numpy as np
from ConfigSpace.types import NotSet, i64


def cli_to_configspace(
    input_data: str, name: str = None
) -> ConfigSpace.ConfigurationSpace:
    """Attempts to process CLI help string to a ConfigSpace representation.

    Args:
        input_data: CLI help string containing parameter data.
        name: Name to give to the ConfigSpace

    Returns:
        ConfigSpace object.
    """
    space = ConfigSpace.ConfigurationSpace(name=name)

    parameter_data = []
    first_group = False
    for line in input_data.split("\n"):
        line = line.strip()
        if line == "":
            first_group = False
        if line.startswith("-"):
            first_group = True
            parameter_data.append(line)
        elif not first_group:
            continue
        else:
            parameter_data[-1] = parameter_data[-1] + " " + line
    if not parameter_data:
        return space
    name_pattern = r"(?<!\S)--?[\w-]+"
    int_min, int_max = (
        int(np.iinfo(i64).min / 10),
        int(np.iinfo(i64).max / 10),
    )  # ConfigSpace bug on positive max size? Also causes an error during sampling
    float_min, float_max = -sys.maxsize, sys.maxsize
    print(
        "For each parameter we need to know the parameter type, please choose for each found out of the following:"
    )
    print(
        "\t- Integer\n\t- Float\n\t- Ordinal\n\t- Categorical\n\t- Boolean\n\t- Empty/Skip [Do not add this parameter]\n"
    )
    for parameter in parameter_data:
        matches = re.findall(name_pattern, parameter)
        for match in matches:
            name = match.strip("-")
            if (
                len(name) == 1 and len(matches) > 1
            ):  # Short version of the parameter, continue
                continue
            break

        print(f"\nParameter [{name}]: ")
        print(f"Description: {parameter}")
        value = input("Please specify the parameter type: ")
        if value.lower() in ["", "empty", "skip"]:
            print("> Skipping parameter...")
            continue
        default = input(
            "Please specify the parameter default value (Empty for not set): "
        )
        if default == "":
            default = NotSet

        match value.lower():
            case "integer" | "int" | "1":  # Integer
                lower, upper = None, None
                while lower is None or upper is None:
                    user_input = input(
                        "Please specify the integer lower and upper limit separated by a comma (,). Empty defaults to -max / max: "
                    )
                    if "," in user_input:
                        lower, upper = user_input.split(",", maxsplit=1)
                lower, upper = lower.strip(), upper.strip()
                lower = int_min if lower == "" else i64(lower)
                upper = int_max if upper == "" else i64(upper)
                default = int(default) if default != NotSet else None
                log = (
                    input("Should the values be sampled on a log-scale? (y/n): ").lower()
                    == "y"
                )
                try:
                    space.add(
                        ConfigSpace.UniformIntegerHyperparameter(
                            name=name,
                            lower=lower,
                            upper=upper,
                            default_value=default,
                            log=log,
                            meta=parameter,
                        )
                    )
                except Exception as e:
                    print("The following exception occured: ", e)
                    print("Continuing to the next parameter...")
                    continue
            case "float" | "2":  # Float
                lower, upper = None, None
                while lower is None or upper is None:
                    user_input = input(
                        "Please specify the float lower and upper limit separated by a comma (,). Empty defaults to -max / max: "
                    )
                    if "," in user_input:
                        lower, upper = user_input.split(",", maxsplit=1)
                lower, upper = lower.strip(), upper.strip()
                lower = float_min if lower == "" else float(lower)
                upper = float_max if upper == "" else float(upper)
                default = float(default) if default != NotSet else None
                log = (
                    input("Should the values be sampled on a log-scale? (y/n): ").lower()
                    == "y"
                )
                try:
                    space.add(
                        ConfigSpace.UniformFloatHyperparameter(
                            name=name,
                            lower=lower,
                            upper=upper,
                            default_value=default,
                            log=log,
                            meta=parameter,
                        )
                    )
                except Exception as e:
                    print("The following exception occured: ", e)
                    print("Continuing to the next parameter...")
                    continue
            case "ordinal" | "ord" | "3":  # Ordinal
                print(
                    "Please specify the ordinal ascending sequence separated by a comma (,): ",
                    end="",
                )
                sequence = [
                    s.strip()
                    for s in input(
                        "Please specify the ordinal ascending sequence separated by a comma (,): "
                    ).split(",")
                ]
                if default != NotSet:
                    while default not in sequence:
                        default = input(
                            "Please specify the default value from the sequence: "
                        )
                elif default not in sequence:
                    print(
                        "The default value is not in the sequence, please specify a new default value, or leave empty to add it to the sequence."
                    )
                    while default != "" or default not in sequence:
                        default = input("Default value: ")
                    if default == "":
                        sequence.append(default)
                try:
                    space.add(
                        ConfigSpace.OrdinalHyperparameter(
                            name=name,
                            sequence=sequence,
                            default_value=default,
                            meta=parameter,
                        )
                    )
                except Exception as e:
                    print("The following exception occured: ", e)
                    print("Continuing to the next parameter...")
                    continue
            case "categorical" | "cat" | "4":  # Categorical
                choices = [
                    s.strip()
                    for s in input(
                        "Please specify the categorical options separated by a comma (,): "
                    ).split(",")
                ]
                choices = [option.strip() for option in choices]
                if default != NotSet:
                    while default not in choices:
                        default = input(
                            "Please specify the default value from the choices: "
                        )
                elif default not in choices:
                    print(
                        "The default value is not in the choices, please specify a new default value, or leave empty to add it to the choices."
                    )
                    while default != "" or default not in choices:
                        default = input("Default value: ")
                    if default == "":
                        choices.append(default)
                try:
                    space.add(
                        ConfigSpace.CategoricalHyperparameter(
                            name=name,
                            choices=choices,
                            default_value=default,
                            meta=parameter,
                        )
                    )
                except Exception as e:
                    print("The following exception occured: ", e)
                    print("Continuing to the next parameter...")
                    continue
            case "boolean" | "bool" | "5":  # Boolean
                if default != NotSet:
                    while default not in ["True", "False"]:
                        default = input(
                            "Please specify the default value as True/False: "
                        )
                space.add(
                    ConfigSpace.CategoricalHyperparameter(
                        name=name,
                        choices=["True", "False"],
                        default_value=default,
                    )
                )
            case _:  # Skip
                continue
    return space


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser(
        description="Command to wrap input solvers and feature extractors."
        "Specify a path to the directory containing your solvers."
    )
    parser.add_argument(*ac.WrapTypeArgument.names, **ac.WrapTypeArgument.kwargs)
    parser.add_argument(*ac.WrapPathArgument.names, **ac.WrapPathArgument.kwargs)
    parser.add_argument(*ac.WrapTargetArgument.names, **ac.WrapTargetArgument.kwargs)
    parser.add_argument(
        *ac.WrapGeneratePCSArgument.names, **ac.WrapGeneratePCSArgument.kwargs
    )
    return parser


def main(argv: list[str]) -> None:
    """Main entry point of the Check command."""
    parser = parser_function()
    args = parser.parse_args(argv)
    settings = gv.settings(args)

    # Log command call
    sl.log_command(sys.argv, settings.random_state)
    type_map = {
        "extractor": Extractor,
        "feature-extractor": Extractor,
        "solver": Solver,
        "Extractor": Extractor,
        "Feature-Extractor": Extractor,
        "Solver": Solver,
        "FeatureExtractor": Extractor,
    }

    if args.type not in type_map:
        options_text = "\n".join([f"\t- {value}" for value in type_map.keys()])
        raise ValueError(
            f"Unknown type {args.type}. Please choose from:\n{options_text}"
        )
    type = type_map[args.type]

    print(f"Wrapping {type.__name__} in directory {args.path} ...")
    path: Path = args.path
    if not path.exists():
        raise ValueError(f"Directory {path} does not exist.")

    target_path: Path = args.target
    if (
        path not in target_path.parents
    ):  # Allow the user to flexibly specify the target (as path/executable or just executable)
        target_path = path / args.target

    if not target_path.exists():
        raise ValueError(f"Target executable {target_path} does not exist.")

    if type == Solver:
        target_wrapper = path / (
            Solver._wrapper_file + Settings.DEFAULT_solver_wrapper_template.suffix
        )
        if target_wrapper.exists():
            print(f"WARNING: Wrapper {target_wrapper} already exists. Skipping...")
        else:
            template_data = Settings.DEFAULT_solver_wrapper_template.open().read()
            template_data = template_data.replace(
                "@@@YOUR_EXECUTABLE_HERE@@@", str(target_path.relative_to(path))
            )
            target_wrapper.open("w").write(template_data)
            target_wrapper.chmod(0o755)  # Set read and execution rights for all
        if args.generate_pcs:
            pcs_file: Path = path / "sparkle_PCS.yaml"
            if pcs_file.exists():
                print(f"WARNING: PCS file {pcs_file} already exists. Skipping...")
            else:
                solver_call = subprocess.run(
                    [str(target_path), "--help"], capture_output=True
                )
                input_data = (
                    solver_call.stdout.decode("utf-8")
                    + "\n"
                    + solver_call.stderr.decode("utf-8")
                )
                space = cli_to_configspace(input_data, name=target_path.stem)
                if len(space) == 0:  # Failed to extract anything
                    print(
                        "Could not extract any parameters from the executable. No PCS file was created."
                    )
                    sys.exit(-1)
                space.to_yaml(pcs_file)
    elif type == Extractor:
        raise NotImplementedError("Feature extractor wrapping not implemented yet.")

    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
