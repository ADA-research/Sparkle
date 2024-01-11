#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# import os
import sys
import subprocess
from pathlib import Path


executable_name = r'fastvc2+p'

relative_path = sys.argv[1]
minvc_instance_file = sys.argv[2]
cutoff_time_str = sys.argv[3]
seed_str = r'1'
para_str = " ".join(sys.argv[4:])

# command_line = os.path.join(relative_path, executable_name) + r' -inst ' + minvc_instance_file + r' -seed ' + seed_str + r' -cutoff_time ' + cutoff_time_str + r' -opt 0 ' + para_str
cmd_list = [Path(relative_path) / Path(executable_name), 
            "-inst", minvc_instance_file, 
            "-seed", seed_str,
            "-cutoff_time", cutoff_time_str,
            "-opt 0", para_str]
# os.system(command_line)
subprocess.run(cmd_list)
