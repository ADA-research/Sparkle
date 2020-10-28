#!/bin/bash

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/validate_configured_vs_default.sh
#SBATCH --output=TMP/validate_configured_vs_default.sh.txt
#SBATCH --error=TMP/validate_configured_vs_default.sh.err
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

smac_settings_path="Settings/sparkle_smac_settings.txt"
smac_settings_tmp="Settings/sparkle_smac_settings.tmp"
smac_settings_test="Commands/test/test_files/sparkle_smac_settings.txt"
mv $smac_settings_path $smac_settings_tmp # Save user settings
cp $smac_settings_test $smac_settings_path # Activate test settings

# Prepare for test
instances_path_train="Examples/Resources/Instances/PTN/"
instances_path_test="Examples/Resources/Instances/PTN2/"
solver_path="Examples/Resources/Solvers/PbO-CCSAT-Generic/"
configuration_results_path="Commands/test/test_files/results/"
smac_path="Components/smac-v2.10.03-master-778/"

Commands/initialise.py > /dev/null
Commands/add_instances.py --run-solver-later --run-extractor-later $instances_path_train > /dev/null
Commands/add_instances.py --run-solver-later --run-extractor-later $instances_path_test > /dev/null
Commands/add_solver.py --run-solver-later --deterministic 0 $solver_path > /dev/null

# Copy configuration results to simulate the configuration command
cp -r $configuration_results_path $smac_path

# Test configured solver and default solver with both train and test sets
output=$(Commands/validate_configured_vs_default.py --solver $solver_path --instance-set-train $instances_path_train --instance-set-test $instances_path_test | tail -1)

if [[ $output =~ [0-9] ]];
then
	echo "[success] validate_configured_vs_default with both train and test sets test succeeded"
else              
	echo "[failure] validate_configured_vs_default with both train and test sets test failed with output:"
	echo $output
fi

# Test configured solver and default solver with just training set
output=$(Commands/validate_configured_vs_default.py --solver $solver_path --instance-set-train $instances_path_train | tail -1)

if [[ $output =~ [0-9] ]];
then
	echo "[success] validate_configured_vs_default with just training set test succeeded"
else              
	echo "[failure] validate_configured_vs_default with just training set test failed with output:"
	echo $output
fi

# Restore original settings
mv $slurm_settings_tmp $slurm_settings_path
mv $smac_settings_tmp $smac_settings_path

