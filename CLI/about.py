#!/usr/bin/env python3
"""Sparkle command to show information about Sparkle."""

import sys
import sparkle_logging as sl

import sparkle

if __name__ == "__main__":
    # Log command call
    sl.log_command(sys.argv)

    print("\n".join([
        f"Sparkle ({sparkle.about.description})",
        f"Version: {sparkle.about.version}",
        f"Licence: {sparkle.about.licence}",
        f'Written by {", ".join(sparkle.about.authors[:-1])},\
            and {sparkle.about.authors[-1]}',
        f"Contact: {sparkle.about.contact}",
        "For more details see README.md"]))
