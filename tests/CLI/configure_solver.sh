#!/bin/bash

# Import utils
. tests/CLI/utils.sh

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/configure_solver.sh
#SBATCH --output=Tmp/configure_solver.sh.txt
#SBATCH --error=Tmp/configure_solver.sh.err
#SBATCH --partition=graceADA
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1

slurm_true="slurm"
slurm_available=$(detect_slurm)

# Settings
sparkle_test_settings_path="tests/CLI/test_files/Settings/sparkle_settings.ini"

# Prepare for test
examples_path="Examples/Resources/"
instances_path="Instances/PTN/"
solver_path="Solvers/PbO-CCSAT-Generic/"
instances_src_path="${examples_path}${instances_path}"
solver_src_path="${examples_path}${solver_path}"

sparkle/CLI/initialise.py > /dev/null
sparkle/CLI/add_instances.py $instances_src_path > /dev/null
sparkle/CLI/add_solver.py $solver_src_path > /dev/null

# Set up output conditions
output_true="Running configuration finished!"
if [[ $slurm_available =~ "${slurm_true}" ]];
then
	output_true="Running configuration. Waiting for Slurm job(s) with id(s): "
fi

# Configure solver
output=$(sparkle/CLI/configure_solver.py --solver $solver_path --instance-set-train $instances_path --settings-file $sparkle_test_settings_path --run-on $slurm_available | tail -1)

if [[ $output =~ "${output_true}" ]];
then
	echo "[success] ($slurm_available) configure_solver test succeeded"
    jobid=${output##* }
	if [[ $slurm_available =~ "${slurm_true}" ]];
	then
		scancel $jobid
	fi
else
	echo "[failure] ($slurm_available) configure_solver test failed with output:"
	echo $output
    if [[ $slurm_available =~ "${slurm_true}" ]];
	then
		kill_started_jobs_slurm
	fi
fi

sleep 1 # Sleep to avoid interference from previous test

# Configure solver with objective PAR10
output=$(sparkle/CLI/configure_solver.py --solver $solver_path --instance-set-train $instances_path --objectives PAR10 --settings-file $sparkle_test_settings_path --run-on $slurm_available | tail -1)

if [[ $output =~ "${output_true}" ]];
then
	echo "[success] ($slurm_available) configure_solver performance measure RUNTIME option test succeeded"
    jobid=${output##* }
	if [[ $slurm_available =~ "${slurm_true}" ]];
	then
		scancel $jobid
	fi
else
	echo "[failure] ($slurm_available) configure_solver performance measure RUNTIME option test failed with output:"
	echo $output
    if [[ $slurm_available =~ "${slurm_true}" ]];
	then
		kill_started_jobs_slurm
	fi
fi

sleep 1 # Sleep to avoid interference from previous test

# TODO: Add test: Configure solver with performance measure option QUALITY (needs a quality configuration solver+instances)

# Configure solver with cutoff time option
output=$(sparkle/CLI/configure_solver.py --solver $solver_path --instance-set-train $instances_path --target-cutoff-time 3 --settings-file $sparkle_test_settings_path --run-on $slurm_available | tail -1)

if [[ $output =~ "${output_true}" ]];
then
	echo "[success] ($slurm_available) configure_solver cutoff time option test succeeded"
    jobid=${output##* }
	if [[ $slurm_available =~ "${slurm_true}" ]];
	then
		scancel $jobid
	fi
else
	echo "[failure] ($slurm_available) configure_solver cutoff time option test failed with output:"
	echo $output
    if [[ $slurm_available =~ "${slurm_true}" ]];
	then
		kill_started_jobs_slurm
	fi
fi

sleep 1 # Sleep to avoid interference from previous test

# Configure solver with budget per run option
output=$(sparkle/CLI/configure_solver.py --solver $solver_path --instance-set-train $instances_path --wallclock-time 10 --settings-file $sparkle_test_settings_path --run-on $slurm_available | tail -1)

if [[ $output =~ "${output_true}" ]];
then
	echo "[success] ($slurm_available) configure_solver budget per run option test succeeded"
    jobid=${output##* }
	if [[ $slurm_available =~ "${slurm_true}" ]];
	then
		scancel $jobid
	fi
else
	echo "[failure] ($slurm_available) configure_solver budget per run option test failed with output:"
	echo $output
	if [[ $slurm_available =~ "${slurm_true}" ]];
	then
		kill_started_jobs_slurm
	fi
fi

sleep 1 # Sleep to avoid interference from previous test

# Configure solver with number of runs option
output=$(sparkle/CLI/configure_solver.py --solver $solver_path --instance-set-train $instances_path --number-of-runs 5 --settings-file $sparkle_test_settings_path --run-on $slurm_available | tail -1)

if [[ $output =~ "${output_true}" ]];
then
	echo "[success] ($slurm_available) configure_solver number of runs option test succeeded"
    jobid=${output##* }
	if [[ $slurm_available =~ "${slurm_true}" ]];
	then
		scancel $jobid
	fi
else
	echo "[failure] ($slurm_available) configure_solver number of runs option test failed with output:"
	echo $output
    if [[ $slurm_available =~ "${slurm_true}" ]];
	then
		kill_started_jobs_slurm
	fi
fi
