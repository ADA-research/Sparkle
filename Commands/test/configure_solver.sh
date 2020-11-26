#!/bin/bash

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/configure_solver.sh
#SBATCH --output=TMP/configure_solver.sh.txt
#SBATCH --error=TMP/configure_solver.sh.err
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
instances_path="Examples/Resources/Instances/PTN/"
solver_path="Examples/Resources/Solvers/PbO-CCSAT-Generic/"

Commands/initialise.py > /dev/null
Commands/add_instances.py --run-solver-later --run-extractor-later $instances_path > /dev/null
Commands/add_solver.py --run-solver-later --deterministic 0 $solver_path > /dev/null

# Configure solver
output=$(Commands/configure_solver.py --solver $solver_path --instance-set-train $instances_path | tail -1)

if [[ $output =~ [0-9] ]];
then
	echo "[success] configure_solver test succeeded"
else              
	echo "[failure] configure_solver test failed with output:"
	echo $output
fi

# Configure solver with performance measure option RUNTIME
output=$(Commands/configure_solver.py --solver $solver_path --instance-set-train $instances_path --performance-measure RUNTIME | tail -1)

if [[ $output =~ [0-9] ]];
then
	echo "[success] configure_solver performance measure RUNTIME option test succeeded"
else              
	echo "[failure] configure_solver performance measure RUNTIME option test failed with output:"
	echo $output
fi

# TODO: Add test: Configure solver with performance measure option QUALITY (needs a quality configuration solver+instances)

# Configure solver with cutoff time option
output=$(Commands/configure_solver.py --solver $solver_path --instance-set-train $instances_path --cutoff-time 3 | tail -1)

if [[ $output =~ [0-9] ]];
then
	echo "[success] configure_solver cutoff time option test succeeded"
else              
	echo "[failure] configure_solver cutoff time option test failed with output:"
	echo $output
fi

# Configure solver with budget option
output=$(Commands/configure_solver.py --solver $solver_path --instance-set-train $instances_path --budget 10 | tail -1)

if [[ $output =~ [0-9] ]];
then
	echo "[success] configure_solver budget option test succeeded"
else              
	echo "[failure] configure_solver budget option test failed with output:"
	echo $output
fi

# Restore original settings
mv $slurm_settings_tmp $slurm_settings_path
mv $smac_settings_tmp $smac_settings_path

