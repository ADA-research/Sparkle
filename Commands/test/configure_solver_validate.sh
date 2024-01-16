#!/bin/bash

# Import utils
. Commands/test/utils.sh

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
sparkle_test_settings_path="Commands/test/test_files/sparkle_settings.ini"
slurm_true="slurm"
slurm_available=$(detect_slurm)

# Prepare for test
examples_path="Examples/Resources/"
instances_path="Instances/PTN/"
solver_path="Solvers/PbO-CCSAT-Generic/"
instances_src_path="${examples_path}${instances_path}"
solver_src_path="${examples_path}${solver_path}"

Commands/initialise.py > /dev/null
Commands/add_instances.py $instances_src_path > /dev/null
Commands/add_solver.py --deterministic 0 $solver_src_path > /dev/null

# Set up output validation
output_true="Running configuration finished!"
if [[ $slurm_available =~ "${slurm_true}" ]];
then
    output_true="Running configuration in parallel. Waiting for Slurm job(s) with id(s): "
fi

# Configure solver
output=$(Commands/configure_solver.py --validate --ablation --solver $solver_path --instance-set-train $instances_path --settings-file $sparkle_test_settings_path --run-on $slurm_available | tail -1)

validationcallbackfile=Tmp/delayed_validation_PbO-CCSAT-Generic_PTN_script.sh
ablationcallbackfile=Tmp/delayed_ablation_PbO-CCSAT-Generic_PTN_script.sh
if [ ! -f "$validationcallbackfile" ]; then
    echo "[failure] ($slurm_available) $validationcallbackfile does not exist for configure_solver_validation."
    if [[ $slurm_available =~ "${slurm_true}" ]];
	then
		kill_started_jobs_slurm
	fi
elif [ ! -f "$ablationcallbackfile" ]; then
    echo "[failure] ($slurm_available) $ablationcallbackfile does not exist for configure_solver_validation."
    if [[ $slurm_available =~ "${slurm_true}" ]];
	then
		kill_started_jobs_slurm
	fi
elif [[ $output =~ "${output_true}" ]]; then
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
