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
slurm_settings_path="Settings/sparkle_slurm_settings.txt"
slurm_settings_tmp="Settings/sparkle_slurm_settings.tmp"
slurm_settings_test="CLI/test/test_files/sparkle_slurm_settings.txt"
mv $slurm_settings_path $slurm_settings_tmp # Save user settings
cp $slurm_settings_test $slurm_settings_path # Activate test settings

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

configuration_results_path="CLI/test/test_files/results"
smac_path="Components/smac-v2.10.03-master-778/"
smac_results_path="${smac_path}results/"
smac_results_path_tmp="${smac_path}results/"

CLI/initialise.py > /dev/null
CLI/add_instances.py $instances_src_path_train > /dev/null
CLI/add_instances.py $instances_src_path_test > /dev/null
CLI/add_solver.py --deterministic 0 $solver_src_path > /dev/null

mv $smac_results_path $smac_results_path_tmp &> /dev/null # Save user results

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

# Copy configuration results to simulate the configuration command (it won't have finished yet)
cp -r $configuration_results_path $smac_path # Place test results

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

rm -r $smac_results_path # Remove test results
mv $smac_results_path_tmp $smac_results_path &> /dev/null # Restore user results
mv $slurm_settings_tmp $slurm_settings_path # Restore original settings
