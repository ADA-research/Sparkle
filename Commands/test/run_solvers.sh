#!/bin/bash

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/run_solvers.sh
#SBATCH --output=TMP/run_solvers.sh.txt
#SBATCH --error=TMP/run_solvers.sh.err
#SBATCH --partition=graceADA
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1

# Activate environment
source activate sparkle_test &> /dev/null

# Prepare for test
instances_path="Examples/Resources/Instances/SAT_test"
solver_path="Examples/Resources/Solvers/CSCCSat/"

Commands/initialise.py > /dev/null
Commands/add_instances.py --run-solver-later --run-extractor-later $instances_path > /dev/null
Commands/add_solver.py --run-solver-later --deterministic 0 $solver_path > /dev/null

# Run solvers
output_true="c Running solvers done!"
output=$(Commands/run_solvers.py | tail -1)

if [[ $output == $output_true ]];
then
	echo "[success] run_solvers test succeeded"
else
	echo "[failure] run_solvers test failed with output:"
	echo $output
fi

