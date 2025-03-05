"""This module provides tools for the argument parsing for solver wrappers."""
from pathlib import Path
import ast
from typing import Any

from sparkle.types import resolve_objective


def parse_commandline_dict(args: list[str]) -> dict:
    """Parses a commandline dictionary to the object."""
    dict_str = " ".join(args)
    dict_str = dict_str[dict_str.index("{"):dict_str.index("}") + 1]  # Slurm script fix
    return ast.literal_eval(dict_str)


def parse_solver_wrapper_args(args: list[str]) -> dict[Any]:
    """Parse the arguments passed to the solver wrapper.

    Args:
        args: a list of arguments passed via the command line. It is ensured by Sparkle
            that this list contains certain keys such as `solver_dir`.

    Returns:
        A dictionary mapping argument names to their currently held values.
    """
    args_dict = parse_commandline_dict(args)

    # Some data needs specific formatting
    args_dict["solver_dir"] = Path(args_dict["solver_dir"])
    args_dict["instance"] = Path(args_dict["instance"])
    args_dict["seed"] = int(args_dict["seed"])
    args_dict["objectives"] = [resolve_objective(name)
                               for name in args_dict["objectives"].split(",")]
    args_dict["cutoff_time"] = float(args_dict["cutoff_time"])

    if "config_path" in args_dict:
        # The arguments were not directly given and must be parsed from a file
        config_str = Path(args_dict["config_path"]).open("r")\
            .readlines()[args_dict["seed"]]
        # Extract the args without any quotes
        config_split = [arg.strip().replace("'", "").replace('"', "").strip("-")
                        for arg in config_str.split(" -") if arg.strip() != ""]
        for arg in config_split:
            varname, value = arg.strip("'").strip('"').split(" ", maxsplit=1)
            args_dict[varname] = value
        del args_dict["config_path"]

    return args_dict


def get_solver_call_params(args_dict: dict,
                           prefix: str = "-",
                           postfix: str = " ") -> list[str]:
    """Gather the additional parameters for the solver call.

    Args:
        args_dict: Dictionary mapping argument names to their currently held values
        prefix: Prefix of the command line options
        postfix: Postfix of the command line options

    Returns:
        A list of parameters for the solver call
    """
    params = []
    # Certain arguments are not relevant/have already been processed
    ignore_args = {"solver_dir", "instance", "cutoff_time", "seed", "objectives"}
    for key in args_dict:
        if key not in ignore_args and args_dict[key] is not None:
            if postfix == " ":
                params.extend([prefix + str(key), str(args_dict[key])])
            else:
                params.extend([prefix + str(key) + postfix + str(args_dict[key])])

    return params
