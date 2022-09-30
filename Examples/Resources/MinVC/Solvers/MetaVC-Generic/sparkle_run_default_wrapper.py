#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import argparse

# Problem specific imports
import fcntl
import sys


# Print a command line call for the target algorithm with a given instance file
def print_command(instance_file, seed_str: str, cutoff_time_str: str):
    executable_name = 'MetaVC'
    param_str = "-opt '0' -print_sol '1' -edge_weight_p_scale '0.5214052710418935' -edge_weight_threshold_scale '0.414990365260387' -init_sol '1' -perform_adding_random_walk '0' -perform_bms '0' -perform_cc_adding '1' -perform_edge_weight_scheme '1' -perform_preprocess '1' -perform_removing_random_walk '0' -perform_ruin_and_reconstruct '0' -sel_adding_v '4' -sel_edge_weight_scheme '1' -sel_removing_v '2' -sel_uncov_e '1' -tabu_tenure '5'"

    command_line = executable_name + ' -inst ' + instance_file + ' -seed ' + seed_str + ' ' + param_str

    print(command_line)


# Parse problem specific output and print it for Sparkle; or ask Sparkle to use it's own parser (SAT only)
def print_output(terminal_output_file: str):
    # Read solution quality from file
    infile = open(terminal_output_file, 'r')
    fcntl.flock(infile.fileno(), fcntl.LOCK_EX)

    solution_quality = sys.maxsize
    status = 'UNKNOWN'
    lines = infile.readlines()

    for line in lines:
        words = line.strip().split()
        if len(words) <= 0:
            continue
        if len(words) >=4 and words[1] == 'c' and words[2] == 'vertex_cover:':
            temp_solution_quality = int(words[3])
            if solution_quality < 0 or temp_solution_quality < solution_quality:
                solution_quality = temp_solution_quality
                status = 'SUCCESS'

    infile.close()

    # [required for quality objective] Print keyword 'quality' followed by a space and the solution quality
    print('quality ' + str(solution_quality))
    # [optional] Print keyword 'status' followed by a space and the run status
    print('status ' + status)


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
