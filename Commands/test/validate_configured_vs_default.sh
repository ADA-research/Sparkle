#!/bin/bash

# Import utils
. Commands/test/utils.sh

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
slurm_settings_path="Settings/sparkle_slurm_settings.txt"
slurm_settings_tmp="Settings/sparkle_slurm_settings.tmp"
slurm_settings_test="Commands/test/test_files/sparkle_slurm_settings.txt"
mv $slurm_settings_path $slurm_settings_tmp # Save user settings
cp $slurm_settings_test $slurm_settings_path # Activate test settings

sparkle_test_settings_path="Commands/test/test_files/sparkle_settings.ini"

# Prepare for test
instances_path_train="Examples/Resources/Instances/PTN/"
instances_path_test="Examples/Resources/Instances/PTN2/"
solver_path="Examples/Resources/Solvers/PbO-CCSAT-Generic/"
configuration_results_path="Commands/test/test_files/results/"
configuration_files_path="Commands/test/test_files/PbO-CCSAT-Generic/PTN_train.txt"
smac_path="Components/smac-v2.10.03-master-778/"
smac_configuration_files_path="$smac_path/example_scenarios/PbO-CCSAT-Generic/"

Commands/initialise.py > /dev/null
Commands/add_instances.py $instances_path_train > /dev/null
Commands/add_instances.py $instances_path_test > /dev/null
Commands/add_solver.py --deterministic 0 $solver_path > /dev/null

# Copy configuration results and other files to simulate the configuration command
cp -r $configuration_results_path $smac_path
mkdir -p $smac_configuration_files_path # Make sure directory exists
cp $configuration_files_path $smac_configuration_files_path

# Test configured solver and default solver with both train and test sets
output=$(Commands/validate_configured_vs_default.py --solver $solver_path --instance-set-train $instances_path_train --instance-set-test $instances_path_test --settings-file $sparkle_test_settings_path | tail -1)
output_true="c Running validation in parallel. Waiting for Slurm job with id: "

if [[ $output =~ [^$output_true] ]];
then
	echo "[success] validate_configured_vs_default with both train and test sets test succeeded"
    jobid=${output##* }
	scancel $jobid
else              
	echo "[failure] validate_configured_vs_default with both train and test sets test failed with output:"
	echo $output
    kill_started_jobs_slurm
fi

# Test configured solver and default solver with just training set
output=$(Commands/validate_configured_vs_default.py --solver $solver_path --instance-set-train $instances_path_train --settings-file $sparkle_test_settings_path | tail -1)

if [[ $output =~ [^$output_true] ]];
then
	echo "[success] validate_configured_vs_default with just training set test succeeded"
    jobid=${output##* }
	scancel $jobid
else              
	echo "[failure] validate_configured_vs_default with just training set test failed with output:"
	echo $output
    kill_started_jobs_slurm
fi

# Restore original settings
mv $slurm_settings_tmp $slurm_settings_path

