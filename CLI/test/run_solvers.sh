#!/bin/bash

# Import utils
. CLI/test/utils.sh

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/run_solvers.sh
#SBATCH --output=Tmp/run_solvers.sh.txt
#SBATCH --error=Tmp/run_solvers.sh.err
#SBATCH --partition=graceADA
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1

# Settings
sparkle_test_settings_path="CLI/test/test_files/sparkle_settings.ini"

# Prepare for test
instances_path="Examples/Resources/Instances/PTN"
solver_path="Examples/Resources/Solvers/CSCCSat/"

CLI/initialise.py > /dev/null
CLI/add_instances.py $instances_path > /dev/null
CLI/add_solver.py --deterministic 0 $solver_path > /dev/null

# Run solvers
output_true="Running solvers done!"
output=$(CLI/run_solvers.py --run-on=local --settings-file $sparkle_test_settings_path | tail -1)

if [[ $output == $output_true ]];
then
	echo "[success] run_solvers test succeeded"
else
	echo "[failure] run_solvers test failed with output:"
	echo $output
fi

# Run solvers recompute and parallel
output_true="Running solvers in parallel. Waiting for Slurm job(s) with id(s): "
output=$(CLI/run_solvers.py --run-on=slurm --settings-file $sparkle_test_settings_path --parallel --recompute | tail -1)

if [[ $output =~ "${output_true}" ]];
then
	echo "[success] run_solvers --parallel --recompute test succeeded"
    jobid=${output##* }
	scancel $jobid
else
	echo "[failure] run_solvers --parallel --recompute test failed with output:"
	echo $output
    kill_started_jobs_slurm
fi

# Run solvers with verifier
output=$(CLI/run_solvers.py --run-on=slurm --settings-file $sparkle_test_settings_path --parallel --recompute --verifier SAT | tail -1)

if [[ $output =~ "${output_true}" ]];
then
	echo "[success] run_solvers --parallel --recompute --verifier SAT test succeeded"
    jobid=${output##* }
	scancel $jobid
else
	echo "[failure] run_solvers --parallel --recompute --verifier SAT test failed with output:"
	echo $output
    kill_started_jobs_slurm
fi

