#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Template for users to create Feature Extractor wrappers."""

import sys
import ast
import subprocess
from pathlib import Path

# Convert the argument of the feature extractor script to dictionary
args = ast.literal_eval(" ".join(sys.argv[1:]))

# Extract and delete data that needs specific formatting
extractor_dir = Path(args["extractor_dir"])
input_file = Path(args["input_file"])
output_file = Path(args["output_file"])

del args["extractor_dir"]
del args["input_file"]
del args["output_file"]

extractor_name = "YourExtractor"  # Change this to the extractor's name
if extractor_dir != Path("."):
    extractor_exec = f"{extractor_dir / extractor_name}"
else:
    f"./{extractor_name}"
extractor_cmd = [extractor_exec,
                "-input", str(input_file),
                "-output", str(output_file)]

# Construct call from args dictionary
params = []
for key in args:
    if args[key] is not None:
        params.extend(["-" + str(key), str(args[key])])

try:
    extractor_call = subprocess.run(extractor_cmd + params,
                                    capture_output=True)
except Exception as ex:
    print(f"Extractor call failed with exception:\n{ex}")

# If needed, further processing of the extractor output can be added here

outdir = {"status": "SUCCESS",
          "feature_file": output_file}

print(outdir)
