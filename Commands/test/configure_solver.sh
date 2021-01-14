#!/bin/bash

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/configure_solver.sh
#SBATCH --output=Tmp/configure_solver.sh.txt
#SBATCH --error=Tmp/configure_solver.sh.err
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
instances_path="Examples/Resources/Instances/PTN/"
solver_path="Examples/Resources/Solvers/PbO-CCSAT-Generic/"

Commands/initialise.py > /dev/null
Commands/add_instances.py --run-solver-later --run-extractor-later $instances_path > /dev/null
Commands/add_solver.py --run-solver-later --deterministic 0 $solver_path > /dev/null

# Configure solver
output=$(Commands/configure_solver.py --solver $solver_path --instance-set-train $instances_path --settings-file $sparkle_test_settings_path | tail -1)

if [[ $output =~ [0-9] ]];
then
	echo "[success] configure_solver test succeeded"
else              
	echo "[failure] configure_solver test failed with output:"
	echo $output
fi

# Configure solver with performance measure option RUNTIME
output=$(Commands/configure_solver.py --solver $solver_path --instance-set-train $instances_path --performance-measure RUNTIME --settings-file $sparkle_test_settings_path | tail -1)

if [[ $output =~ [0-9] ]];
then
	echo "[success] configure_solver performance measure RUNTIME option test succeeded"
else              
	echo "[failure] configure_solver performance measure RUNTIME option test failed with output:"
	echo $output
fi

# TODO: Add test: Configure solver with performance measure option QUALITY (needs a quality configuration solver+instances)

# Configure solver with cutoff time option
output=$(Commands/configure_solver.py --solver $solver_path --instance-set-train $instances_path --target-cutoff-time 3 --settings-file $sparkle_test_settings_path | tail -1)

if [[ $output =~ [0-9] ]];
then
	echo "[success] configure_solver cutoff time option test succeeded"
else              
	echo "[failure] configure_solver cutoff time option test failed with output:"
	echo $output
fi

# Configure solver with budget per run option
output=$(Commands/configure_solver.py --solver $solver_path --instance-set-train $instances_path --budget-per-run 10 --settings-file $sparkle_test_settings_path | tail -1)

if [[ $output =~ [0-9] ]];
then
	echo "[success] configure_solver budget per run option test succeeded"
else              
	echo "[failure] configure_solver budget per run option test failed with output:"
	echo $output
fi

# Configure solver with number of runs option
output=$(Commands/configure_solver.py --solver $solver_path --instance-set-train $instances_path --number-of-runs 5 --settings-file $sparkle_test_settings_path | tail -1)

if [[ $output =~ [0-9] ]];
then
	echo "[success] configure_solver number of runs option test succeeded"
else              
	echo "[failure] configure_solver number of runs option test failed with output:"
	echo $output
fi

# Restore original settings
mv $slurm_settings_tmp $slurm_settings_path

