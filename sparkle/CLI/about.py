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
    print("\n".join([
          f"Sparkle ({sparkle.about.description})",
          f"Version: {sparkle.about.version}",
          f"Licence: {sparkle.about.licence}",
          f'Written by {", ".join(sparkle.about.authors[:-1])},\
           and {sparkle.about.authors[-1]}',
          f"Contact: {sparkle.about.contact}",
          "For more details see README.md"]))
    sys.exit()


if __name__ == "__main__":
    main(sys.argv[1:])
