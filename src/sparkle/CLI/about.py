#!/usr/bin/env python3
"""Sparkle command to show information about Sparkle."""

import sys
import argparse
import sparkle.__about__


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments.

    Returns:
      The argument parser.
    """
    parser = argparse.ArgumentParser("Show information about Sparkle.")
    return parser


def main(argv: list[str]) -> None:
    """Main function of the command."""
    authors = sparkle.__about__.authors.split(", ")
    print(
        "\n".join(
            [
                f"Sparkle ({sparkle.__about__.description})",
                f"Version: {sparkle.__about__.__version__}",
                f"Licence: {sparkle.__about__.licence}",
                f"Written by {', '.join(authors[:-1])} and {authors[-1]}",
                f"Contact: {sparkle.__about__.contact}",
                "For more details see README.md",
            ]
        )
    )
    sys.exit()


if __name__ == "__main__":
    main(sys.argv[1:])
