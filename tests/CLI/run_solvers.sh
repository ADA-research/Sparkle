#!/bin/bash

# Import utils
. tests/CLI/utils.sh

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
sparkle_test_settings_path="tests/CLI/test_files/Settings/sparkle_settings.ini"

# Prepare for test
instances_path="Examples/Resources/Instances/PTN"
solver_path="Examples/Resources/Solvers/CSCCSat/"

sparkle/CLI/initialise.py > /dev/null
sparkle/CLI/add_instances.py $instances_path > /dev/null
sparkle/CLI/add_solver.py $solver_path > /dev/null

# Run solvers
output_true="Running solvers done!"
output=$(sparkle/CLI/run_solvers.py --run-on=local --settings-file $sparkle_test_settings_path | tail -1)

if [[ $output == $output_true ]];
then
	echo "[success] run_solvers local test succeeded"
else
	echo "[failure] run_solvers local test failed with output:"
	echo $output
fi

# Run solvers recompute and parallel
output_true="Running solvers. Waiting for Slurm job(s) with id(s): "
output=$(sparkle/CLI/run_solvers.py --run-on=slurm --settings-file $sparkle_test_settings_path --recompute | tail -1)

if [[ $output =~ "${output_true}" ]];
then
	echo "[success] run_solvers --recompute test succeeded"
    jobid=${output##* }
	scancel $jobid
else
	echo "[failure] run_solvers --recompute test failed with output:"
	echo $output
    kill_started_jobs_slurm
fi

# Run solvers with verifier
output=$(sparkle/CLI/run_solvers.py --run-on=slurm --settings-file $sparkle_test_settings_path --recompute | tail -1)

if [[ $output =~ "${output_true}" ]];
then
	echo "[success] run_solvers --recompute test succeeded"
    jobid=${output##* }
	scancel $jobid
else
	echo "[failure] run_solvers --recompute test failed with output:"
	echo $output
    kill_started_jobs_slurm
fi
