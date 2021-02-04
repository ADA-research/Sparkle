#!/bin/bash

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
instances_path="Examples/Resources/Instances/PTN/"
instances_path_two="Examples/Resources/Instances/PTN2/"
solver_path="Examples/Resources/Solvers/PbO-CCSAT-Generic/"
configuration_results_path="Commands/test/test_files/results/"
smac_path="Components/smac-v2.10.03-master-778/"
smac_configuration_files_path="$smac_path/example_scenarios/PbO-CCSAT-Generic/"

Commands/initialise.py > /dev/null
Commands/add_instances.py --run-solver-later --run-extractor-later $instances_path > /dev/null
Commands/add_instances.py --run-solver-later --run-extractor-later $instances_path_two > /dev/null
Commands/add_solver.py --run-solver-later --deterministic 0 $solver_path > /dev/null

# Copy configuration results to simulate the configuration command (it won't have finished yet)
cp -r $configuration_results_path $smac_path

# Configure solver
output=$(Commands/configure_solver.py --solver $solver_path --instance-set-train $instances_path_two --settings-file $sparkle_test_settings_path --ablation | tail -1)

if [[ $output =~ [0-9] ]];
then
	echo "[success] configure_solver with sequential ablation run test succeeded"
else
	echo "[failure] configure_solver with sequential ablation run test failed with output:"
	echo $output
fi

# Run ablation on train set
output=$(Commands/run_ablation.py --solver $solver_path --instance-set-train $instances_path | tail -1)

if [[ $output =~ [0-9] ]];
then
	echo "[success] run_ablation test succeeded"
else              
	echo "[failure] run_ablation test failed with output:"
	echo $output
fi

# Run ablation on test set
output=$(Commands/run_ablation.py --solver $solver_path --instance-set-train $instances_path --instance-set-test $instances_path_two | tail -1)

if [[ $output =~ [0-9] ]];
then
	echo "[success] run_ablation with test set test succeeded"
else
	echo "[failure] run_ablation with test set test failed with output:"
	echo $output
fi

# Restore original settings
mv $slurm_settings_tmp $slurm_settings_path
