#!/bin/bash

# Import utils
. Commands/test/utils.sh

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
slurm_settings_test="Commands/test/test_files/sparkle_slurm_settings.txt"
mv $slurm_settings_path $slurm_settings_tmp # Save user settings
cp $slurm_settings_test $slurm_settings_path # Activate test settings

sparkle_test_settings_path="Commands/test/test_files/sparkle_settings.ini"

# Prepare for test
examples_path="Examples/Resources/"
instances_path_train="Instances/PTN/"
instances_path_test="Instances/PTN2/"
solver_path="Solvers/PbO-CCSAT-Generic/"
instances_src_path_train="${examples_path}${instances_path_train}"
instances_src_path_test="${examples_path}${instances_path_test}"
solver_src_path="${examples_path}${solver_path}"

configuration_results_path="Commands/test/test_files/results/"
smac_path="Components/smac-v2.10.03-master-778/"
smac_results_path="${smac_path}results/"
smac_results_path_tmp="${smac_path}results_tmp/"

Commands/initialise.py > /dev/null
Commands/add_instances.py $instances_src_path_train > /dev/null
Commands/add_instances.py $instances_src_path_test > /dev/null
Commands/add_solver.py --deterministic 0 $solver_src_path > /dev/null

mv $smac_results_path $smac_results_path_tmp &> /dev/null # Save user results

# Configure solver
output=$(Commands/configure_solver.py --solver $solver_path --instance-set-train $instances_path_train --settings-file $sparkle_test_settings_path --ablation | tail -1)
output_true="c Running configuration in parallel. Waiting for Slurm job(s) with id(s): "

if [[ $output =~ "${output_true}" ]];
then
	echo "[success] configure_solver with sequential ablation run test succeeded"
    jobid=${output##* }
    echo $output
	scancel $jobid
else
	echo "[failure] configure_solver with sequential ablation run test failed with output:"
	echo $output
    kill_started_jobs_slurm
fi

# Copy configuration results to simulate the configuration command (it won't have finished yet)
cp -r $configuration_results_path $smac_path # Place test results

# Run ablation on train set
output=$(Commands/run_ablation.py --solver $solver_path --instance-set-train $instances_path_train | tail -1)
output_true="c Ablation analysis running. Waiting for Slurm job(s) with id(s): "

if [[ $output =~ "${output_true}" ]];
then
	echo "[success] run_ablation test succeeded"
    jobid=${output##* }
    echo $output
	scancel $jobid
else              
	echo "[failure] run_ablation test failed with output:"
	echo $output
    kill_started_jobs_slurm
fi

# Run ablation on test set
output=$(Commands/run_ablation.py --solver $solver_path --instance-set-train $instances_path_train --instance-set-test $instances_path_test | tail -1)

if [[ $output =~ "${output_true}" ]];
then
	echo "[success] run_ablation with test set test succeeded"
    jobid=${output##* }
    echo $output
	scancel $jobid
else
	echo "[failure] run_ablation with test set test failed with output:"
	echo $output
    kill_started_jobs_slurm
fi

rm -r $smac_results_path # Remove test results
mv $smac_results_path_tmp $smac_results_path &> /dev/null # Restore user results
mv $slurm_settings_tmp $slurm_settings_path # Restore original settings
