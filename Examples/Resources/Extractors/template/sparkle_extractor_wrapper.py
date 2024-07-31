#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Template for users to create Feature Extractor wrappers."""

import time
import sys
import random
import argparse
import subprocess
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("-features", action="store_true",
                    help="Only print features and their groups as a list of tuples.")
parser.add_argument("-extractor_dir", type=str, help="Path to the extractor directory")
parser.add_argument("-instance_file", type=str, help="Path to the instance file")
# You can add the "feature_group" argument if you want to allow parallelisation of
# computation on a single instance.
# You will need to write code to handle the computation of a single feature group
# by your extractor.
# parser.add_argument("-feature_group", type=str, help="The feature group to compute for
# this instance. If not present, all will be computed.")
parser.add_argument("-output_file", type=str, help="Path to the output file")
args = parser.parse_args()

# Define your feature names as {output_feature_name: (feature_group, feature_name)}
# (Optional) Map your feature names to the Sparkle feature enums to unify your extractor
# with various other extractors
feature_mapping = {}

if args.features:
    # Return a list of feature names and their feature groups as
    # [(feature_group, feature_name), ...]
    print([feature_mapping[key] for key in feature_mapping.keys()])
    sys.exit()

extractor_dir = args.extractor_dir
instance_path = args.instance_file
output_file = args.output_file

# Set this to your executable descriptions or place your python code here
extractor_name = "Example"
executable_name = "features"
executable = Path(extractor_dir) / executable_name

raw_result_file_name = Path(
    f"{extractor_dir}{executable_name}_"
    f"{Path(instance_path).name}_"
    f"{time.strftime('%Y%m%d-%H%M%S')}_{int(random.getrandbits(32))}"
    ".rawres")
tmp_output = Path("TMP") / raw_result_file_name

command_line = [Path(extractor_dir) / executable_name, instance_path, tmp_output]

subprocess.run(command_line, stdout=raw_result_file_name.open("w+"))

# Read all lines from the raw output file
raw_text = Path(raw_result_file_name).read_text()

# Process raw result file and write to the final result file
with open(output_file, "w") as out_file:
    # Do some post processing if needed here
    out_file.write(raw_text)

# Deletes temporary files
raw_result_file_name.unlink(missing_ok=True)
