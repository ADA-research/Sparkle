#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""MetaVC-Generic solver wrapper."""
import sys
import subprocess
from pathlib import Path
from sparkle.types import SolverStatus
from sparkle.tools.solver_wrapper_parsing import parse_solver_wrapper_args

# Convert the arguments to a dictionary
args = parse_solver_wrapper_args(sys.argv[1:])

# Extract and delete data that needs specific formatting
solver_dir = Path(args["solver_dir"])
instance = Path(args["instance"])
seed = args["seed"]
cutoff = args["cutoff_time"]

del args["solver_dir"]
del args["instance"]
del args["cutoff_time"]
del args["seed"]

solver_name = "MetaVC"
if solver_dir != Path("."):
    solver_exec = f"{solver_dir / solver_name}"
else:
    f"./{solver_name}"

'''
c Usage: ./MetaVC   (*Required*)
c -inst <instance_name>   (*Required*)
c -seed <seed>   (*Required*)
c -opt <target_optimal_size>
c -print_sol {0, 1}   (Default: 0) [Print solution]
c -perform_preprocess {0, 1}   (Default: 1)
c -init_sol {1, 2}   (Default: 1)
c -perform_ruin_and_reconstruct {0, 1}   (Default: 0)
c -prob_ruin_and_reconstruct [0, 1]   (Default: 0.001)
c -num_vertex_ruin_and_reconstruct {int, from 1 to 100}   (Default: 10)
c -perform_removing_random_walk {0, 1}   (Default: 0)
c -removing_prob_random_walk [0, 1]   (Default: 0.05)
c -perform_bms {0, 1}   (Default: 0)
c -bms_k {int, from 20 to 1000}   (Default: 50)
c -sel_removing_v {1, 2, 3, 4, 5, 6, 7, 8, 9}   (Default: 1)
c -tabu_tenure {int, from 1 to 100}   (Default: 3)
c -removing_prob_novelty [0, 1]   (Default: 0.5)
c -prob_distri_c1 [2, 10]   (Default: 2.15)
c -prob_distri_c2 {int, from 1 to 10}   (Default: 4)
c -prob_distri_c3 {int, from 10000 to 1000000}   (Default: 75000)
c -perform_adding_random_walk {0, 1}   (Default: 0)
c -adding_prob_random_walk [0, 1]   (Default: 0.05)
c -perform_cc_adding {0, 1}   (Default: 1)
c -sel_adding_v {1, 2, 3, 4, 5, 6}   (Default: 1)
c -adding_prob_novelty [0, 1]   (Default: 0.5)
c -sel_uncov_e {1, 2}   (Default: 1)
c -perform_edge_weight_scheme {0, 1}   (Default: 1)
c -sel_edge_weight_scheme {1, 2, 3, 4}   (Default: 1)
c -edge_weight_threshold_scale [0, 1]   (Default: 0.5)
c -edge_weight_p_scale [0, 1]   (Default: 0.3)
c -edge_weight_q_scale [0, 1]   (Default: 0.7)
c -paws_smooth_probability [0, 1]   (Default: 0.8)
c -paws_periodical_step_length {int, from 50 to 10000}   (Default: 200)
c -perform_vertex_weight_scheme {0, 1}   (Default: 0)
c -sel_vertex_weight_scheme {1, 2}   (Default: 1)
c -twmvc_smooth_probability [0, 1]   (Default: 0.01)
c -twmvc_delta {int, from 1000 to 1000000}   (Default: 100000)
c -twmvc_beta [0, 1]   (Default: 0.8)
c -twmvc_periodical_step_length {int, from 50 to 10000}   (Default: 100)
'''

solver_cmd = [solver_exec,
              "-inst", str(instance),
              "-seed", str(seed)]

# Construct call from args dictionary
params = []
for key in args:
    if args[key] is not None:
        params.extend(["-" + str(key), str(args[key])])

try:
    solver_call = subprocess.run(solver_cmd + params,
                                 capture_output=True)
except Exception as ex:
    print(f"Solver call failed with exception:\n{ex}")

# Convert Solver output to dictionary for configurator target algorithm script
output_str = solver_call.stdout.decode()
# Optional: Print original output so the solution can be verified by SATVerifier
print(output_str)

solution_quality = sys.maxsize
status = SolverStatus.UNKNOWN

for line in output_str.splitlines():
    words = line.strip().split()
    if len(words) <= 0:
        continue
    if len(words) >= 4 and words[1] == 'c' and words[2] == 'vertex_cover:':
        temp_solution_quality = int(words[3])
        if solution_quality < 0 or temp_solution_quality < solution_quality:
            solution_quality = temp_solution_quality
            status = SolverStatus.SUCCESS

outdir = {"status": status.value,
          "quality": solution_quality,
          "solver_call": solver_cmd + params}

print(outdir)
