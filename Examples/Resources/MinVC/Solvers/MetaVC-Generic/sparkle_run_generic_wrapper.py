#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import sys

executable_name = r'MetaVC'

relative_path = sys.argv[1]
minvc_instance_file = sys.argv[2]
seed_str = r'1'
para_str = r''

len_argv = len(sys.argv)
for i in range(3, len_argv):
	para_str += r' ' + sys.argv[i]

command_line = relative_path+'/'+executable_name + r' -inst ' + minvc_instance_file + r' -seed ' + seed_str + r' ' + para_str

os.system(command_line)