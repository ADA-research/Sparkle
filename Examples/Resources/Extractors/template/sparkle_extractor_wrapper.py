#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Extractor wrapper for SAT2012."""
import sys
import argparse
from enum import Enum
import subprocess
from pathlib import Path

parser = argparse.ArgumentParser(description="Handle I/O for the extractor.")
parser.add_argument("-features", action="store_true", help="Argument to return the features this extractor provides (Group + name, as list of tuples)")
parser.add_argument("-extractor_dir", type=str, help="Path to the extractor directory")
parser.add_argument("-instance_file", type=str, help="Path to the instance file")
parser.add_argument("-output_file", type=str, help="Path to the output file")
args = parser.parse_args()

# TODO: Define possible feature mappings here, consisting of a group and feature name (tuple)

feature_mapping = {}

if args.features:
    # Print the stringified features and the group they belong to
    print([(feature_mapping[key][0].value, feature_mapping[key][1].value
           if isinstance(feature_mapping[key][1], Enum) else feature_mapping[key][1])
           for key in feature_mapping.keys()])
    sys.exit()

extractor_dir = Path(args.extractor_dir)
instance_path = Path(args.instance_file)
output_file = Path(args.output_file) if args.output_file else None

extractor_name = ... # Name of the extractor
executable_name = "features"  # name of the executable
executable = extractor_dir / executable_name  # path to the executable

extractor = subprocess.run([extractor_dir / executable_name, instance_path],
                           capture_output=True)

if extractor.returncode != 0:  # Error handling, TODO: Possible more errors
    print(extractor.stdout.decode())
    print(extractor.stderr.decode())
    sys.exit(extractor.returncode)

# Read all lines from the input file
raw_lines = extractor.stdout.decode().splitlines()

# Process raw result file and write to the final result file
processed_features = []
for i, feature in enumerate(features):
    feature_group, feature_name = feature_mapping[feature]
    if isinstance(feature_name, Enum):
        feature_name = feature_name.value
    processed_features.append((feature_group.value, feature_name, values[i]))  # Results must be returned as a list of TUPLES

if output_file is not None:
    with open(output_file, "w") as out_file:
        out_file.write(str(processed_features))
else:
    print(processed_features)
