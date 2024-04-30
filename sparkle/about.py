"""Helper module for information about Sparkle."""

name = "Sparkle"
version = "0.8.1"
description = "Platform for evaluating empirical algorithms/solvers"
licence = "MIT"
authors = ["Koen van der Blom",
           "Jeremie Gobeil",
           "Holger H. Hoos",
           "Chuan Luo",
           "Richard Middelkoop",
           "Jeroen Rook",
           "Thijs Snelleman",
           ]
contact = "snelleman@aim.rwth-aachen.de"

about_str = f"{name}-{version}"


def print_about() -> None:
    """Print the about str."""
    print(about_str)
