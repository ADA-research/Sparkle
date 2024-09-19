"""Generate shell scripts from markdown files."""

from pathlib import Path
from sparkle import about

if __name__ == "__main__":
    files = [p for p in Path("../Examples").iterdir() if p.is_file() and p.suffix == ".md"]

    for file in files:
        with file.open() as f:
            input_lines = f.readlines()
        output_lines = []
        code_block = False
        for line in input_lines:
            if line.startswith("```"):
                code_block = not code_block
                continue
            if not code_block:
                if line.strip() != "" and line[0] != "#":
                    line = "# " + line
            output_lines.append(line)
            
        with file.with_suffix(".sh").open("w") as f:
            f.write("#!/usr/bin/env bash\n")
            f.write("# Auto-Generated .sh files from the original .md by "
                    f"Sparkle {about.version}")
            f.writelines(output_lines)
