#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import sys

relative_path = sys.argv[1]
minvc_instance_file = sys.argv[2]
cutoff_time_str = sys.argv[3]

executable_name = r'fastvc2+p'
runsolver_name = 'runsolver'
runsolver_option = r'--timestamp --use-pty'
cutoff_time_each_run_option = r'-C ' + cutoff_time_str
runsolver_watch_data_path_option = '-w /dev/null'

seed_str = r'1'
para_str = r"-cand_count '198'"

command_line = os.path.join(relative_path, executable_name) + r' -inst ' + minvc_instance_file + r' -seed ' + seed_str + r' -cutoff_time ' + cutoff_time_str + r' -opt 0 ' + para_str

command_line = os.path.join(relative_path, runsolver_name) + r' ' + runsolver_option + r' ' + cutoff_time_each_run_option + r' ' + runsolver_watch_data_path_option + r' ' + command_line

res = os.popen(command_line)
info = res.readlines()

my_runtime = 0
my_solution_quality = sys.maxsize

for myline in info:
    mylist = myline.strip().split()
    if len(mylist) <= 0:
        continue
    temp_runtime = float(mylist[0].split('/')[0])
    if len(mylist) >=4 and mylist[1] == 'c' and mylist[2] == 'vertex_cover:':
        temp_solution_quality = int(mylist[3])
        if my_solution_quality < 0 or temp_solution_quality < my_solution_quality:
            my_solution_quality = temp_solution_quality
            my_runtime = temp_runtime

print(my_solution_quality, my_runtime)