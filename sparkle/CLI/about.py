#!/usr/bin/env python3
"""Sparkle command to show information about Sparkle."""

import sys
import argparse
import sparkle


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments.

    Returns:
      The argument parser.
    """
    parser = argparse.ArgumentParser("Show information about Sparkle.")
    return parser


def main(argv: list[str]) -> None:
    """Main function of the command."""
    print(
        "\n".join(
            [
                f"Sparkle ({sparkle.description})",
                f"Version: {sparkle.__version__}",
                f"Licence: {sparkle.licence}",
                f"Written by {', '.join(sparkle.authors[:-1])},\
           and {sparkle.authors[-1]}",
                f"Contact: {sparkle.contact}",
                "For more details see README.md",
            ]
        )
    )
    sys.exit()


if __name__ == "__main__":
    main(sys.argv[1:])
