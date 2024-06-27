#!/bin/bash

# Import utils
. CLI/test/utils.sh

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/validate_configured_vs_default.sh
#SBATCH --output=Tmp/validate_configured_vs_default.sh.txt
#SBATCH --error=Tmp/validate_configured_vs_default.sh.err
#SBATCH --partition=graceADA
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1

# Settings
sparkle_test_settings_path="CLI/test/test_files/sparkle_settings.ini"
slurm_true="slurm"
slurm_available=$(detect_slurm)

# Prepare for test
examples_path="Examples/Resources/"
instances_path_train="Instances/PTN/"
instances_path_test="Instances/PTN2/"
solver_path="Solvers/PbO-CCSAT-Generic/"
instances_src_path_train="${examples_path}${instances_path_train}"
instances_src_path_test="${examples_path}${instances_path_test}"
solver_src_path="${examples_path}${solver_path}"

config_scenario_path="Output/Configuration/Raw_Data/SMAC2/scenarios/"
config_test_data="CLI/test/test_files/Output/Configuration/Raw_Data/SMAC2/scenarios/PbO-CCSAT-Generic_PTN"

CLI/initialise.py > /dev/null
CLI/add_instances.py $instances_src_path_train > /dev/null
CLI/add_instances.py $instances_src_path_test > /dev/null
CLI/add_solver.py --deterministic False $solver_src_path > /dev/null

# Copy configuration results and other files to simulate the configuration command
mkdir -p $config_scenario_path
cp -r $config_test_data $config_scenario_path

# Test configured solver and default solver with both train and test sets
output=$(CLI/validate_configured_vs_default.py --solver $solver_path --instance-set-train $instances_path_train --instance-set-test $instances_path_test --settings-file $sparkle_test_settings_path --run-on $slurm_available | tail -1)

output_true="Running validation done!"
if [[ $slurm_available =~ "${slurm_true}" ]];
then
	output_true="RunRunner Submitted a run to Slurm (job "
fi

if [[ $output =~ "${output_true}" ]];
then
	echo "[success] ($slurm_available) validate_configured_vs_default with both train and test sets test succeeded"
    jobid=$(echo "$output" | tr -d -c 0-9)
	if [[ $slurm_available =~ "${slurm_true}" ]];
	then
		scancel $jobid
	fi
else
	echo "[failure] ($slurm_available) validate_configured_vs_default with both train and test sets test failed with output:"
	echo $output
    if [[ $slurm_available =~ "${slurm_true}" ]];
	then
		kill_started_jobs_slurm
	fi
fi

# Test configured solver and default solver with just training set
output=$(CLI/validate_configured_vs_default.py --solver $solver_path --instance-set-train $instances_path_train --settings-file $sparkle_test_settings_path --run-on $slurm_available | tail -1)

if [[ $output =~ "${output_true}" ]];
then
	echo "[success] ($slurm_available) validate_configured_vs_default with just training set test succeeded"
    jobid=$(echo "$output" | tr -d -c 0-9)
	if [[ $slurm_available =~ "${slurm_true}" ]];
	then
		scancel $jobid
	fi
else
	echo "[failure] ($slurm_available) validate_configured_vs_default with just training set test failed with output:"
	echo $output
    if [[ $slurm_available =~ "${slurm_true}" ]];
	then
		kill_started_jobs_slurm
	fi
fi

