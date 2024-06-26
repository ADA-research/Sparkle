#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import argparse


# Print a command line call for the target algorithm with a given instance file
def print_command(instance_file, seed_str: str, cutoff_time_str: str):
    executable_name = 'PbO-CCSAT'
    param_str = "-init_solution '1' -p_swt '0.3' -perform_aspiration '1' -perform_clause_weight '1' -perform_double_cc '1' -perform_first_div '0' -perform_pac '0' -q_swt '0.0' -sel_clause_div '1' -sel_clause_weight_scheme '1' -sel_var_break_tie_greedy '2' -sel_var_div '3' -threshold_swt '300'"

    command_line = executable_name + ' -inst ' + instance_file + ' -seed ' + seed_str + ' ' + param_str

    print(command_line)


# Parse problem specific output and print it for Sparkle; or ask Sparkle to use it's own parser (SAT only)
def print_output(terminal_output_file):
    print('Use Sparkle SAT parser')


### No editing needed for your own wrapper below this line ###


if __name__ == '__main__':
    # Define command line arguments
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--print-command', metavar='INSTANCE_FILE', type=str, help='print command line call to the target algorithm to stdout given an instance file')
    group.add_argument('--print-output', metavar='TERMINAL_OUTPUT_FILE', type=str, help='print target algorithm output in Sparkle format given an output file containing what the algorithm wrote to the terminal')
    parser.add_argument('--seed', metavar='VALUE', type=str, help='required with --print-command; seed for the target algorithm to use')
    parser.add_argument('--cutoff-time', metavar='VALUE', type=str, help='optional with --print-command; cutoff time in seconds for the target algorithm')

    # Process command line arguments
    args = parser.parse_args()
    if args.print_command and args.seed is None:
        parser.error('--print-command requires --seed')
    instance_file = args.print_command
    terminal_output_file = args.print_output
    seed_str = args.seed
    cutoff_time_str = args.cutoff_time

    # Call function based on arguments
    if(instance_file is not None):
        print_command(instance_file, seed_str, cutoff_time_str)
    elif(terminal_output_file is not None):
        print_output(terminal_output_file)

