#!/bin/bash

# Import utils
. CLI/test/utils.sh

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/configure_solver.sh
#SBATCH --output=Tmp/run_ablation.sh.txt
#SBATCH --error=Tmp/run_ablation.sh.err
#SBATCH --partition=graceADA
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1

# Prerequisites
# - Initialise.py
# - Added instances
# - Added solver

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
validation_scenario_path="Output/Validation/"
config_test_data="CLI/test/test_files/Output/Configuration/Raw_Data/SMAC2/scenarios/PbO-CCSAT-Generic_PTN"
validation_train_data="CLI/test/test_files/Output/Validation/PbO-CCSAT-Generic_PTN/"
validation_test_data="CLI/test/test_files/Output/Validation/PbO-CCSAT-Generic_PTN2/"

CLI/initialise.py > /dev/null
CLI/add_instances.py $instances_src_path_train > /dev/null
CLI/add_instances.py $instances_src_path_test > /dev/null
CLI/add_solver.py --deterministic False $solver_src_path > /dev/null

# Copy configuration results and other files to simulate the configuration command
# Prepare configuration scenario output files
mkdir -p $config_scenario_path # Make sure directory exists
mkdir -p $validation_scenario_path
cp -r $config_test_data $config_scenario_path
cp -r $validation_train_data $validation_scenario_path
cp -r $validation_test_data $validation_scenario_path

# Configure solver
output=$(CLI/configure_solver.py --solver $solver_path --instance-set-train $instances_path_train --settings-file $sparkle_test_settings_path --ablation --run-on $slurm_available | tail -1)
output_true="Running configuration in parallel. Waiting for Slurm job(s) with id(s): "
if ! [[ $slurm_available =~ "${slurm_true}" ]];
then
	output_true="Running configuration finished!"
fi

if [[ $output =~ "${output_true}" ]];
then
	echo "[success] ($slurm_available) configure_solver with sequential ablation run test succeeded"
    jobid=${output##* }
	if [[ $slurm_available =~ "${slurm_true}" ]];
	then
		scancel $jobid
	fi
else
	echo "[failure] ($slurm_available) configure_solver with sequential ablation run test failed with output:"
	echo $output
    if [[ $slurm_available =~ "${slurm_true}" ]];
	then
		kill_started_jobs_slurm
	fi
fi

# Re-Copy configuration results and other files to simulate the configuration command
# Prepare configuration scenario output files
mkdir -p $config_scenario_path # Make sure directory exists
mkdir -p $validation_scenario_path
cp -r $config_test_data $config_scenario_path
cp -r $validation_train_data $validation_scenario_path
cp -r $validation_test_data $validation_scenario_path

# Run ablation on train set
output=$(CLI/run_ablation.py --solver $solver_path --instance-set-train $instances_path_train --run-on $slurm_available | tail -1)
output_true="Ablation analysis "

if [[ $output =~ "${output_true}" ]];
then
	echo "[success] ($slurm_available) run_ablation test succeeded"
    jobid=${output##* }
	if [[ $slurm_available =~ "${slurm_true}" ]];
	then
		scancel $jobid
	fi
else
	echo "[failure] ($slurm_available) run_ablation test failed with output:"
	echo $output
    if [[ $slurm_available =~ "${slurm_true}" ]];
	then
		kill_started_jobs_slurm
	fi
fi



# Run ablation on test set
output=$(CLI/run_ablation.py --solver $solver_path --instance-set-train $instances_path_train --instance-set-test $instances_path_test --run-on $slurm_available | tail -1)

if [[ $output =~ "${output_true}" ]];
then
	echo "[success] ($slurm_available) run_ablation with test set test succeeded"
    jobid=${output##* }
	if [[ $slurm_available =~ "${slurm_true}" ]];
	then
		scancel $jobid
	fi
else
	echo "[failure] ($slurm_available) run_ablation with test set test failed with output:"
	echo $output
	if [[ $slurm_available =~ "${slurm_true}" ]];
	then
		kill_started_jobs_slurm
	fi
fi

#rm -rf $config_scenario_path # Remove test results
#rm -rf $validation_scenario_path
mv $smac_results_path_tmp $smac_results_path &> /dev/null # Restore user results
mv $slurm_settings_tmp $slurm_settings_path # Restore original settings
