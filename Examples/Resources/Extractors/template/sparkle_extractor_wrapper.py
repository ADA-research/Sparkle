#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Template for users to create Feature Extractor wrappers."""

import sys
import os
import time
import random
import argparse
import subprocess
from pathlib import Path

parser = argparse.ArgumentParser(description="Process some integers.")
parser.add_argument('-extractor_dir', type=str, help='Path to the extractor directory')
parser.add_argument('-instance_file', type=str, help='Path to the instance file')
parser.add_argument('-output_file', type=str, help='Path to the output file')
args = parser.parse_args()

extractor_dir = args.extractor_dir
instance_path = args.instance_file
output_file = args.output_file

extractor_name = "Example"

executable_name = "features"
executable = Path(extractor_dir) / executable_name

raw_result_file_name = Path(f"{extractor_dir}{executable_name}_" \
                      f"{Path(instance_path).name}_" \
                      f"{time.strftime('%Y%m%d-%H%M%S')}_{int(random.getrandbits(32))}" \
                        ".rawres")
tmp_output = Path("TMP") / raw_result_file_name

command_line = [Path(extractor_dir) / executable_name, instance_path, tmp_output]

subprocess.run(command_line, stdout=raw_result_file_name.open("w+"))

# Read all lines from the input file
raw_lines = Path(raw_result_file_name).read_text().splitlines()

# Process raw result file and write to the final result file
with open(output_file, 'w') as out_file:
    for idx, current_line in enumerate(raw_lines):
        stripped_line = current_line.strip()
        if not stripped_line or stripped_line.startswith('c'):
            continue

        # Split the line by commas, write each part to the output file with additional information
        features = stripped_line.split(',')
        out_file.write(','.join(f',{feature}{extractor_name}' for feature in features) + '\n')

        # Ensure not to go out of index range for the next line
        if idx + 1 < len(raw_lines):
            next_line = raw_lines[idx + 1].strip()
            out_file.write(f'{instance_path},{next_line}\n')

# Deletes temporary files
raw_result_file_name.unlink(missing_ok=True)

