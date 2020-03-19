#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import sys
import random
import time
import pandas as pd
import numpy as np

#print os.getcwd()

executable_name = r'minisat'

relative_path = sys.argv[1]
cnf_instance_file = sys.argv[2]
para_str = r'-no-luby -rinc=1.5 -phase-saving=0 -rnd-freq=0.02'

command_line = relative_path+'/'+executable_name + r' ' + cnf_instance_file + r' ' + para_str

os.system(command_line)

