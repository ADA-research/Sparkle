#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import subprocess
import sys

executable_name = r'MetaVC'

relative_path = sys.argv[1]
minvc_instance_file = sys.argv[2]
seed_str = r'1'
para_list = sys.argv[3:]

#command_line = relative_path+'/'+executable_name + r' -inst ' + minvc_instance_file + r' -seed ' + seed_str + r' ' + " ".join(para_list)
command_line = [relative_path+'/'+executable_name, '-inst', minvc_instance_file, '-seed', seed_str] + para_list

#os.system(command_line)
subprocess.run()