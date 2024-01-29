#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
from pathlib import Path
import subprocess
executable_name = r'TCA'

relative_path = sys.argv[1]
instance_file = sys.argv[2]
cutoff_time = sys.argv[3]
seed_str = r'1'
para_str = " ".join(sys.argv[4:])

cmd_list = [Path(relative_path) / Path(executable_name), instance_file, cutoff_time, seed_str, para_str]
subprocess.run(cmd_list)