"""Command to wrap users' Solvers / Feature extractors for Sparkle."""
import sys
import re
import argparse
from pathlib import Path

from runrunner import Runner

from sparkle.solver import Solver
from sparkle.selector.extractor import Extractor
from sparkle.platform import Settings
from sparkle.types import SolverStatus

from sparkle.CLI.help import logging as sl
from sparkle.CLI.help import argparse_custom as ac
from sparkle.CLI.help import global_variables as gv

import ConfigSpace as cs
from ConfigSpace.types import NotSet


def cli_to_configspace(input_data: str) -> cs.ConfigurationSpace:
    """Attempts to process CLI help string to a ConfigSpace representation.
    
    Args:
        input: CLI help string.

    Returns:
        ConfigSpace object.
    """
    space = cs.ConfigurationSpace()

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
    name_pattern = r"(?<!\S)--?[\w-]+"
    print("For each parameter we need to know the parameter type, please choose for each found name the following:")
    print("1: Integer\n2: Float\n3: Ordinal\n4: Categorical\n5: Boolean\n6: Skip [Do not add this parameter]\n")
    for parameter in parameter_data:
        matches = re.findall(name_pattern, parameter)
        for match in matches:
            name = match.strip("-")
            if len(name) == 1 and len(matches) > 1:  # Short version of the parameter, continue
                continue
            break
        print(f"\nParameter [{name}]: ")
        print(f"Description: {parameter}")
        #print(f"Please specify the parameter type: ", end="")
        value = input(f"Please specify the parameter type: ")
        if value == "6":
            continue
        #print(f"Please specify the parameter default value (Empty for not set): ", end="")
        default = input(f"Please specify the parameter default value (Empty for not set): ")
        if default == "":
            default = NotSet
        match value:
            case "1":  # Integer
                print("Please specify the integer lower and upper limit separated by a comma (,): ", end="")
                lower, upper = input().split(",")
                if default != NotSet:
                    default = int(default)
                space.add_hyperparameter(
                    cs.UniformIntegerHyperparameter(
                        name=name,
                        lower=int(lower),
                        upper=int(upper),
                        default_value=int(default),
                        meta=parameter,
                    )
                )
            case "2":  # Float
                print("Please specify the float lower and upper limit separated by a comma (,): ", end="")
                lower, upper = input().split(",", maxsplit=1)
                space.add_hyperparameter(
                    cs.UniformFloatHyperparameter(
                        name=name,
                        lower=float(lower),
                        upper=float(upper),
                        default_value=float(default),
                        meta=parameter,
                    )
                )
            case "3":  # Ordinal
                print("Please specify the ordinal ascending sequence separated by a comma (,): ", end="")
                sequence = input("Please specify the ordinal ascending sequence separated by a comma (,): ").split(",")
                if default != NotSet:
                    while default not in sequence:
                        default = input("Please specify the default value from the sequence: ")
                space.add_hyperparameter(
                    cs.OrdinalHyperparameter(
                        name=name,
                        sequence=sequence,
                        default_value=default,
                        meta=parameter,
                    )
                )
            case "4":  # Categorical
                choices = input("Please specify the categorical options separated by a comma (,): ").split(",")
                choices = [option.strip() for option in choices]
                if default != NotSet:
                    while default not in choices:
                        default = input("Please specify the default value from the choices: ")
                space.add_hyperparameter(
                    cs.CategoricalHyperparameter(
                        name=name,
                        choices=choices,
                        default_value=default,
                        meta=parameter,
                    )
                )
            case "5":  # Boolean
                if default != NotSet:
                    while default not in ["True", "False"]:
                        default = input("Please specify the default value as True/False: ")
                space.add_hyperparameter(
                    cs.CategoricalHyperparameter(
                        name=name,
                        choices=["True", "False"],
                        default_value=default,
                    )
                )
            case _:  # Skip
                continue
    return cs


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser(
        description="Command to wrap input solvers and feature extractors."
        "Specify a path to the directory containing your solvers."
    )
    parser.add_argument(*ac.WrapPathArgument.names, **ac.WrapPathArgument.kwargs)
    parser.add_argument(*ac.WrapTargetArgument.names, **ac.WrapTargetArgument.kwargs)
    parser.add_argument(*ac.WrapTypeArgument.names, **ac.WrapTypeArgument.kwargs)
    parser.add_argument(*ac.WrapGeneratePCSArgument.names, **ac.WrapGeneratePCSArgument.kwargs)
    # # Settings arguments
    # parser.add_argument(
    #     *Settings.OPTION_solver_cutoff_time.args,
    #     **Settings.OPTION_solver_cutoff_time.kwargs,
    # )
    return parser


def main(argv: list[str]) -> None:
    """Main entry point of the Check command."""
    parser = parser_function()
    args = parser.parse_args(argv)
    settings = gv.settings(args)

    # Log command call
    sl.log_command(sys.argv, settings.random_state)

    print(f"Wrapping {type.__name__} in directory {args.path} ...")
    path: Path = args.path
    if not path.exists():
        raise ValueError(f"Directory {path} does not exist.")

    target_path: Path = path / args.target
    if not target_path.exists():
        raise ValueError(f"Target executable {target_path} does not exist.")

    if args.type == Solver:
        target_wrapper = path / Solver.wrapper
        if target_wrapper.exists():
            print(f"WARNING: Wrapper {target_wrapper} already exists. Skipping...")
        else:
            template_data = Settings.DEFAULT_solver_wrapper_template.open().read()
            template_data = template_data.replace("@@@YOUR_EXECUTABLE_HERE@@@", args.target)
            target_wrapper.open("w").write(template_data)
        if args.generate_pcs:
            pcs_file: Path = path / Solver.pcs_file
            if pcs_file.exists():
                print(f"WARNING: PCS file {pcs_file} already exists. Skipping...")
            else:
                import subprocess
                input_data = subprocess.run([str(target_path), "--help"], capture_output=True).stdout.decode("utf-8")
                cs = cli_to_configspace(input_data)
                cs.to_yaml(pcs_file)
                pcs_file.open("w").write(" ")
    elif args.type == Extractor:
        raise NotImplementedError

    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
