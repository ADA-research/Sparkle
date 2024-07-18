#!/bin/bash

# Import utils
. CLI/test/utils.sh

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/configure_solver_validation.sh
#SBATCH --output=Tmp/configure_solver_validation.sh.txt
#SBATCH --error=Tmp/configure_solver_validation.sh.err
#SBATCH --partition=graceADA
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1

# Settings
sparkle_test_settings_path="CLI/test/test_files/Settings/sparkle_settings.ini"
slurm_true="slurm"
slurm_available=$(detect_slurm)

# Prepare for test
examples_path="Examples/Resources/"
instances_path="Instances/PTN/"
solver_path="Solvers/PbO-CCSAT-Generic/"
instances_src_path="${examples_path}${instances_path}"
solver_src_path="${examples_path}${solver_path}"

CLI/initialise.py > /dev/null
CLI/add_instances.py $instances_src_path > /dev/null
CLI/add_solver.py $solver_src_path > /dev/null

# Set up output validation
output_true="Running configuration finished!"
if [[ $slurm_available =~ "${slurm_true}" ]];
then
    output_true="Running configuration. Waiting for Slurm job(s) with id(s): "
fi

# Configure solver
output=$(CLI/configure_solver.py --validate --ablation --solver $solver_path --instance-set-train $instances_path --settings-file $sparkle_test_settings_path --run-on $slurm_available | tail -1)

if [[ $output =~ "${output_true}" ]]; then
	echo "[success] ($slurm_available) configure_solver_validation test succeeded"
    jobid=${output##* }
    if [[ $slurm_available =~ "${slurm_true}" ]];
	then
		scancel $jobid
	fi
else
	echo "[failure] ($slurm_available) configure_solver_validation test failed with output:"
	echo $output
    if [[ $slurm_available =~ "${slurm_true}" ]];
	then
		kill_started_jobs_slurm
	fi
fi
