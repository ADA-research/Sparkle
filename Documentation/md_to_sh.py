"""Generate shell scripts from markdown files."""

from pathlib import Path


if __name__ == "__main__":
    files = [p for p in Path.iterdir() if p.is_file() and p.suffix == ".md"]

    for file in files:
        with file.open() as f:
            lines = f.readlines()

        with file.with_suffix(".sh").open("w") as f:
            f.write("#!/usr/bin/env bash\n")
            f.writelines(lines)
