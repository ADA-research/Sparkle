#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import sys

executable_name = r'TCA'

relative_path = sys.argv[1]
instance_file = sys.argv[2]
cutoff_time = sys.argv[3]
seed_str = r'1'
para_str = r''

len_argv = len(sys.argv)
for i in range(4, len_argv):
	para_str += r' ' + sys.argv[i]

command_line = os.path.join(relative_path, executable_name) + ' ' + instance_file + ' ' + cutoff_time + ' ' + seed_str + ' ' + para_str

os.system(command_line)