#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import subprocess
import sys

executable_name = r'PbO-CCSAT'

relative_path = sys.argv[1]
cnf_instance_file = sys.argv[2]
seed_str = r'1'
para_list = sys.argv[3:]

# command_line = relative_path+'/'+executable_name + r' -inst ' + cnf_instance_file + r' -seed ' + seed_str + r' ' + " ".join(para_list)
command_line = [relative_path + '/'+ executable_name, '-inst', cnf_instance_file, '-seed', seed_str] + para_list

subprocess.run(command_line)
# os.system(command_line)

