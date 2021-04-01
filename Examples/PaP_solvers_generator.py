#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import os
import sklearn
import sys
from pathlib import Path

from sklearn.utils import shuffle

def shuffle_list(sorted_array: list):
     # The random_state is used to ensure reproducible behaviour.
     return shuffle(sorted_array, random_state=9)

def generation_option_variations(number: int):

    variations_options_list = list()

    init_solution_option = ['1','2']
    option_selection = number % 2
    variations_options_list.append(init_solution_option[option_selection])

    perform_aspiration_option = ['0','1']
    option_selection = int(number/2) % 2
    variations_options_list.append(perform_aspiration_option[option_selection])

    perform_clause_weight_option = ['0','1']
    option_selection = int(number/4) % 2
    variations_options_list.append(perform_clause_weight_option[option_selection])

    perform_double_cc_option = ['0','1']
    option_selection = int(number/8) % 2
    variations_options_list.append(perform_double_cc_option[option_selection])

    perform_first_div_option = ['0','1']
    option_selection = int(number/16) % 2
    variations_options_list.append(perform_first_div_option[option_selection])

    perform_pac_option = ['0','1']
    option_selection = int(number/32) % 2
    variations_options_list.append(perform_pac_option[option_selection])

    p_swt_option = list(range(0, 11))
    p_swt_option = [x/10 for x in p_swt_option]
    option_selection = int(number/64) % 11
    variations_options_list.append(p_swt_option[option_selection])
    # Total options so far = 704

    q_swt_option = list(range(0, 11))
    q_swt_option = [x/10 for x in q_swt_option]
    option_selection = int(number/704) % 11
    variations_options_list.append(q_swt_option[option_selection])

    sel_clause_div_option = ['1','2']
    option_selection = int(number/7744) % 2
    variations_options_list.append(sel_clause_div_option[option_selection])

    sel_clause_weight_scheme_option = ['1','2']
    option_selection = int(number/15488) % 2
    variations_options_list.append(sel_clause_weight_scheme_option[option_selection])

    sel_var_break_tie_greedy_option = list(range(1, 5))
    option_selection = int(number/30976) % 4
    variations_options_list.append(sel_var_break_tie_greedy_option[option_selection])

    sel_var_div_option = list(range(1, 8))
    option_selection = int(number/123904) % 7
    variations_options_list.append(sel_var_div_option[option_selection])

    treshold_swt_option = list(range(10,1001))
    option_selection = int(number/867328) % 990
    variations_options_list.append(treshold_swt_option[option_selection])

    return variations_options_list

def replace_line(file_name, line_num, text):
    lines = open(file_name, 'r').readlines()
    lines[line_num] = text
    out = open(file_name, 'w')
    out.writelines(lines)
    out.close()

def create_solver_variation(number: str, param_str: str, executable_name: str):
    
    directory_path = os.getcwd()
    Solver_directory_path = str(directory_path) + '/Examples/Resources/Solvers/'
    Solver_path = str(directory_path) + '/Examples/Resources/Solvers/' + executable_name + '/'
    new_solver_directory_path = Solver_directory_path + str(executable_name) + '_variation_' + str(number) + '/'

    # copy the directory
    command_line = 'cp -a -r ' + str(Solver_path) + ' ' + str(new_solver_directory_path)
    os.system(command_line)
    changed_file_path = new_solver_directory_path + 'sparkle_run_default_wrapper.py'

    # input the variation into the new directory
    overwrite_line = '\t' + param_str + '\n'
    replace_line(changed_file_path,9,overwrite_line)
    return


if __name__ == r'__main__':

    executable_name = 'PbO-CCSAT-Generic'
    number_of_variations = 3
    variations_options_list = list()
    
    list_of_all_numbers = range(0,858654720)
    shuffled_list_of_all_numbers = shuffle_list(list_of_all_numbers)
    
    for number in range(number_of_variations):

        variations_options_list = generation_option_variations(shuffled_list_of_all_numbers[number])
        param_str = "param_str = \"-init_solution \'" + str(variations_options_list[0]) +  "\' -p_swt \'" + str(variations_options_list[6]) +  "\' -perform_aspiration \'" + str(variations_options_list[1]) + "\' -perform_clause_weight \'" + str(variations_options_list[2]) + "\' -perform_double_cc \'" + str(variations_options_list[3]) + "\' -perform_first_div \'" + str(variations_options_list[4]) + "\' -perform_pac \'" +  str(variations_options_list[5]) + "\' -q_swt \'" + str(variations_options_list[7]) + "\' -sel_clause_div \'" + str(variations_options_list[8]) + "\' -sel_clause_weight_scheme \'" + str(variations_options_list[9]) + "\' -sel_var_break_tie_greedy \'" + str(variations_options_list[10]) + "\' -sel_var_div \'" + str(variations_options_list[11]) + "\' -threshold_swt \'" + str(variations_options_list[12]) + '\'\"'
        create_solver_variation(str(number),param_str,executable_name)