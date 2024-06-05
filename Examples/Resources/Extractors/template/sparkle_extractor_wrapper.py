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

global sparkle_special_string
sparkle_special_string = r'__@@SPARKLE@@__'

def get_last_level_directory_name(filepath):
    return os.path.basename(filepath.rstrip('/'))

def get_time_pid_random_string():
    return f"{time.strftime('%Y%m%d-%H%M%S')}_{os.getpid()}_{random.randint(1000000, 9999999)}"

parser = argparse.ArgumentParser(description="Process some integers.")
parser.add_argument('-extractor_dir', type=str, help='Path to the extractor directory')
parser.add_argument('-instance_file', type=str, help='Path to the instance file')
parser.add_argument('-output_file', type=str, help='Path to the output file')
args = parser.parse_args()

extractor_dir = args.extractor_dir
instance_path = args.instance_file
output_file = args.output_file

executable_name = "features"

raw_result_file_name = f"{extractor_dir}{executable_name}_" \
                      f"{get_last_level_directory_name(instance_path)}_" \
                      f"{get_time_pid_random_string()}.rawres"
tmp_output = f"TMP/{raw_result_file_name}"

command_line = [f"{extractor_dir}/{executable_name}", instance_path, tmp_output]

with Path(raw_result_file_name).open("w+") as raw_result_file:
    subprocess.run(command_line, stdout=raw_result_file)

#Processes raw result file and writes to the final result file
with open(raw_result_file_name, 'r') as fin, open(output_file, 'w') as fout:
        for line in fin:
            # Strip any leading or trailing whitespace from the line.
            line = line.strip()
            if not line:
                continue

            # Split the line into words and skip if the line is empty or starts with 'c'.
            words = line.split()
            if not words or words[0] == 'c':
                continue

            # Splits the line by commas, writes each part to the output file with additional information
            items = line.split(',')
            for item in items:
                fout.write(f',{item}{sparkle_special_string}{get_last_level_directory_name(extractor_dir)}')
            fout.write('\n')

            # Read the next line, strip it, and write it to the output file with instance path.
            next_line = fin.readline().strip()
            fout.write(f'{instance_path},{next_line}\n')

# Deletes temporary files
Path(tmp_output).unlink(missing_ok=True)
Path(raw_result_file_name).unlink(missing_ok=True)

