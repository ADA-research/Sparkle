#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
import subprocess
from pathlib import Path


executable_name = r'fastvc2+p'

relative_path = sys.argv[1]
minvc_instance_file = sys.argv[2]
cutoff_time_str = sys.argv[3]
seed_str = r'1'
para_str = " ".join(sys.argv[4:])

cmd_list = [Path(relative_path) / Path(executable_name), 
            "-inst", minvc_instance_file, 
            "-seed", seed_str,
            "-cutoff_time", cutoff_time_str,
            "-opt 0", para_str]

subprocess.run(cmd_list)
