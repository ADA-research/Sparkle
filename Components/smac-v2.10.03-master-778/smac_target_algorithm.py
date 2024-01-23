#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
import ast
import argparse
import time
import subprocess
from pathlib import Path

from Commands.sparkle_help import sparkle_global_help as sgh


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments given by SMAC."""
    parser = argparse.ArgumentParser(
        description="SMAC input from commandline.")
    parser.add_argument(
        "-init_solution",
        type=int,
        help="Initial solution?"
    )
    parser.add_argument(
        "-p_swt",
        type=float,
        help="p_swt?"
    )
    parser.add_argument(
        "-perform_aspiration",
        type=int,
        help="?"
    )
    parser.add_argument(
        "-perform_clause_weight",
        type=int,
        help="?"
    )
    parser.add_argument(
        "-perform_double_cc",
        type=int,
        help="?"
    )
    parser.add_argument(
        "-perform_first_div",
        type=int,
        help="?"
    )
    parser.add_argument(
        "-perform_pac",
        type=int,
        help="?"
    )
    parser.add_argument(
        "-q_swt",
        type=float,
        help="?"
    )
    parser.add_argument(
        "-sel_clause_div",
        type=int,
        help="?"
    )
    parser.add_argument(
        "-sel_clause_weight_scheme",
        type=int,
        help="?"
    )
    parser.add_argument(
        "-sel_var_break_tie_greedy",
        type=int,
        help="?"
    )
    parser.add_argument(
        "-sel_var_div",
        type=int,
        help="?"
    )
    parser.add_argument(
        "-threshold_swt",
        type=int,
        help="?"
    )
    return parser


if __name__ == "__main__":
    # Incoming call from SMAC:
    # Argsv
    # 0: ../../../smac_target_algorithm.py 
    # 1: ../../../../../Instances/PTN/Ptn-7824-b11.cnf
    # 2: 0
    # 3: 60.0
    # 4: 2147483647
    # 5: 738507
    # 6: 
    #   -init_solution '1'
    #   -p_swt '0.3'
    #   -perform_aspiration '1' 
    #   -perform_clause_weight '1' 
    #   -perform_double_cc '1'
    #   -perform_first_div '0'
    #   -perform_pac '0'
    #   -q_swt '0.0' 
    #   -sel_clause_div '1'
    #   -sel_clause_weight_scheme '1'
    #   -sel_var_break_tie_greedy '2'
    #   -sel_var_div '3'
    #   -threshold_swt '300'
    parser = parser_function()
    args = parser.parse_args(sys.argv[6:])
    args.instance = sys.argv[1]
    args.specifics = sys.argv[2]
    args.cutoff_time = float(sys.argv[3])
    args.run_length = int(sys.argv[4])
    args.seed = int(sys.argv[5])

    start_t = time.time()
    solver = subprocess.run([Path.cwd() / sgh.sparkle_smac_wrapper, str(args)],
                            capture_output=True)
    run_time = min(time.time() - start_t, args.cutoff_time)
    print(solver)
    if solver.returncode != 0:
        print(solver.stderr)
        sys.exit(solver.returncode)
    
    outdir = ast.literal_eval(solver.stdout)
    print(f"Result for SMAC: {outdir['status']}, {run_time}, 0, 0, {args.seed}")