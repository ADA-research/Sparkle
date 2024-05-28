#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Template for users to create Feature Extractor wrappers."""

import sys
import os
import time
import random
import ast
import subprocess
from pathlib import Path

global sparkle_special_string
sparkle_special_string = r'__@@SPARKLE@@__'

def get_last_level_directory_name(filepath):
    return os.path.basename(filepath.rstrip('/'))

def get_time_pid_random_string():
    # Dummy implementation for the sake of completeness
    import time, os, random
    return f"{time.strftime('%Y%m%d-%H%M%S')}_{os.getpid()}_{random.randint(1000000, 9999999)}"

# Convert the argument of the feature extractor script to dictionary
args = ast.literal_eval(" ".join(sys.argv[1:]))

# Extract and delete data that needs specific formatting
extractor_dir = Path(args["extractor_dir"])
instance_path = Path(args["instance_file"])
output_file = Path(args["output_file"])

del args["extractor_dir"]
del args["instance_file"]
del args["output_file"]

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
        while True:
            # Reads every line, strips whitespace and returns on empty line
            myline = fin.readline().strip()
            if not myline:
                break
            
            # Splits the line into single words and skips empty lines & lines starting with 'c'
            mylist = myline.split()
            if len(mylist) == 0 or mylist[0] == 'c':
                continue
            
            # Splits the line by commas, writes each part to the output file with additional information
            mylist_comma = myline.split(',')
            for item in mylist_comma:
                fout.write(f',{item}{sparkle_special_string}{get_last_level_directory_name(extractor_dir)}')
            fout.write('\n')

            myline2 = fin.readline().strip()
            fout.write(f'{instance_path},{myline2}\n')

# Deletes temporary files
Path(tmp_output).unlink(missing_ok=True)
Path(raw_result_file_name).unlink(missing_ok=True)

