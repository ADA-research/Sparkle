#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Template for users to create Feature Extractor wrappers."""
import time
import random
import argparse
import subprocess
from pathlib import Path

global sparkle_special_string
sparkle_special_string = r"__@@SPARKLE@@__"

parser = argparse.ArgumentParser(description="Handle I/O for the extractor.")
parser.add_argument("-extractor_dir", type=str, help="Path to the extractor directory")
parser.add_argument("-instance_file", type=str, help="Path to the instance file")
parser.add_argument("-output_file", type=str, help="Path to the output file")
args = parser.parse_args()

extractor_dir = Path(args.extractor_dir)
instance_path = Path(args.instance_file)
output_file = Path(args.output_file)

extractor_name = "SATFeatureCompetition2012"

executable_name = "features"
executable = extractor_dir / executable_name

raw_result_file_name = Path(f"{extractor_dir}{executable_name}_" \
                            f"{instance_path.name}_{time.strftime('%Y%m%d-%H%M%S')}" \
                            f"_{int(random.getrandbits(32))}.rawres")
tmp_output = Path("TMP") / raw_result_file_name

subprocess.run([extractor_dir / executable_name,
                instance_path,
                tmp_output],
                stdout=raw_result_file_name.open("w+"))

# Read all lines from the input file
raw_lines = Path(raw_result_file_name).read_text().splitlines()

# Process raw result file and write to the final result file
with open(output_file, "w") as out_file:
    if len(raw_lines) >= 2:
        features = raw_lines[-2].strip().split(",")
        values = raw_lines[-1].strip()
        out_file.write(",".join(f"{feature}{sparkle_special_string}{extractor_dir.name}"
                                for feature in features) + "\n")
        out_file.write(f"{instance_path},{values}\n")

# Deletes temporary files
raw_result_file_name.unlink(missing_ok=True)

