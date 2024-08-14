#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import argparse

# Problem specific imports
import fcntl
import sys
from sparkle.types import SolverStatus


# Print a command line call for the target algorithm with a given instance file
def print_command(instance_file, seed_str: str, cutoff_time_str: str):
    executable_name = 'fastvc2+p'
    param_str = "-cand_count '198'"

    # NOTE: This algorithm requires the cutoff time, but to ensure consistent runtime
    # measurements by Sparkle we multiply it by 10 to make sure the algorithm does not
    # stop early, but is stopped by Sparkle (runsolver) consistenty with other solvers
    cutoff_time_str = str(int(cutoff_time_str) * 10)
    command_line = executable_name + ' -inst ' + instance_file + ' -seed ' + seed_str +\
        ' -cutoff_time ' + cutoff_time_str + ' -opt 0 ' + param_str

    print(command_line)


# Parse problem specific output and print it for Sparkle; or ask Sparkle to use it's
# own parser (SAT only)
def print_output(terminal_output_file):
    # Read solution quality from file
    infile = open(terminal_output_file, 'r')
    fcntl.flock(infile.fileno(), fcntl.LOCK_EX)

    solution_quality = sys.maxsize
    status = SolverStatus.UNKNOWN
    lines = infile.readlines()

    for line in lines:
        words = line.strip().split()
        if len(words) <= 0:
            continue
        if len(words) >= 4 and words[1] == 'c' and words[2] == 'Arguments' and \
                words[3] == 'Error!':
            status = SolverStatus.CRASHED
            break
        if len(words) >= 4 and words[1] == 'c' and words[2] == 'vertex_cover:':
            temp_solution_quality = int(words[3])
            if solution_quality < 0 or temp_solution_quality < solution_quality:
                solution_quality = temp_solution_quality
                status = SolverStatus.SUCCESS

    infile.close()

    # [required for quality objective] Print keyword 'quality' followed by a space
    # and the solution quality
    print('quality ' + str(solution_quality))
    # [optional] Print keyword 'status' followed by a space and the run status
    print('status ' + status.value)


# No editing needed for your own wrapper below this line ###


if __name__ == '__main__':
    # Define command line arguments
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--print-command', metavar='INSTANCE_FILE', type=str,
                       help='print command line call to the target algorithm \
                       to stdout given an instance file')
    group.add_argument('--print-output', metavar='TERMINAL_OUTPUT_FILE', type=str,
                       help='print target algorithm output in Sparkle format given an \
                        output file containing what the algorithm wrote to the terminal')
    parser.add_argument('--seed', metavar='VALUE', type=str,
                        help='required with --print-command; seed for the target \
                             algorithm to use')
    parser.add_argument('--cutoff-time', metavar='VALUE', type=str,
                        help='optional with --print-command; cutoff time in \
                              seconds for the target algorithm')

    # Process command line arguments
    args = parser.parse_args()
    if args.print_command and args.seed is None:
        parser.error('--print-command requires --seed')
    instance_file = args.print_command
    terminal_output_file = args.print_output
    seed_str = args.seed
    cutoff_time_str = args.cutoff_time

    # Call function based on arguments
    if (instance_file is not None):
        print_command(instance_file, seed_str, cutoff_time_str)
    elif (terminal_output_file is not None):
        print_output(terminal_output_file)
