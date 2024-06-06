#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Template for users to create Feature Extractor wrappers."""
import time
import random
import argparse
import subprocess
from pathlib import Path

def get_time_random_string():
    return f"{time.strftime('%Y%m%d-%H%M%S')}_{int(random.getrandbits(32))}"

parser = argparse.ArgumentParser(description="Process some integers.")
parser.add_argument('-extractor_dir', type=str, help='Path to the extractor directory')
parser.add_argument('-instance_file', type=str, help='Path to the instance file')
parser.add_argument('-output_file', type=str, help='Path to the output file')
args = parser.parse_args()

extractor_dir = Path(args.extractor_dir)
instance_path = Path(args.instance_file)
output_file = Path(args.output_file)

extractor_name = "SATFeatureCompetition2012"

executable_name = "features"
executable = extractor_dir / executable_name

raw_result_file_name = Path(f"{extractor_dir}{executable_name}_" \
                            f"{instance_path.name}_{get_time_random_string()}.rawres")
tmp_output = Path("TMP") / raw_result_file_name #T.S: Why is this seperately used from raw result? shouldn't there be only one variable describign the raw output?

subprocess.run([extractor_dir / executable_name,
                instance_path,
                tmp_output],
                stdout=raw_result_file_name.open("w+"))

# Read all lines from the input file
raw_lines = Path(raw_result_file_name).read_text().splitlines()

# Process raw result file and write to the final result file
with open(output_file, 'w') as out_file:
    #TS: Don't use this for loop, instead just extract the latest two lines and do some checks to see if they are correct
    # e.g. minor regex, checking if the raw_lines are >=2, 
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
tmp_output.unlink(missing_ok=True)
raw_result_file_name.unlink(missing_ok=True)

