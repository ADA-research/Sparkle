#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import sys

executable_name = r'PbO-CCSAT'

relative_path = sys.argv[1]
cnf_instance_file = sys.argv[2]
seed_str = r'1'
para_str = r''

len_argv = len(sys.argv)
for i in range(3, len_argv):
	para_str += r' ' + sys.argv[i]

command_line = relative_path+'/'+executable_name + r' -inst ' + cnf_instance_file + r' -seed ' + seed_str + r' ' + para_str

os.system(command_line)

