#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import sys

executable_name = r'PbO-CCSAT'

relative_path = sys.argv[1]
cnf_instance_file = sys.argv[2]
seed_str = r'1'
para_str = r"-init_solution '1' -p_swt '0.3' -perform_aspiration '1' -perform_clause_weight '1' -perform_double_cc '1' -perform_first_div '0' -perform_pac '0' -q_swt '0.0' -sel_clause_div '1' -sel_clause_weight_scheme '1' -sel_var_break_tie_greedy '2' -sel_var_div '3' -threshold_swt '300'"

command_line = relative_path+'/'+executable_name + r' -inst ' + cnf_instance_file + r' -seed ' + seed_str + r' ' + para_str

os.system(command_line)

