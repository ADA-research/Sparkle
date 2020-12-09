#!/bin/bash

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/run_solvers.sh
#SBATCH --output=TMP/run_solvers.sh.txt
#SBATCH --error=TMP/run_solvers.sh.err
#SBATCH --partition=graceADA
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1

# Settings
default_settings_path="Settings/sparkle_default_settings.txt"
default_settings_tmp="Settings/sparkle_default_settings.tmp"
default_settings_test="Commands/test/test_files/sparkle_default_settings.txt"
mv $default_settings_path $default_settings_tmp # Save user settings
cp $default_settings_test $default_settings_path # Activate test settings

sparkle_test_settings_path="Commands/test/test_files/sparkle_settings.ini"

# Prepare for test
instances_path="Examples/Resources/Instances/PTN"
solver_path="Examples/Resources/Solvers/CSCCSat/"

Commands/initialise.py > /dev/null
Commands/add_instances.py --run-solver-later --run-extractor-later $instances_path > /dev/null
Commands/add_solver.py --run-solver-later --deterministic 0 $solver_path > /dev/null

# Run solvers
output_true="c Running solvers done!"
output=$(Commands/run_solvers.py --settings-file sparkle_test_settings_path | tail -1)

if [[ $output == $output_true ]];
then
	echo "[success] run_solvers test succeeded"
else
	echo "[failure] run_solvers test failed with output:"
	echo $output
fi

# Run solvers parallel
output=$(Commands/run_solvers.py --settings-file sparkle_test_settings_path --parallel | tail -1)

if [[ $output =~ [0-9] ]];
then
	echo "[success] run_solvers --parallel test succeeded"
else
	echo "[failure] run_solvers --parallel test failed with output:"
	echo $output
fi

# Run solvers recompute
output=$(Commands/run_solvers.py --settings-file sparkle_test_settings_path --parallel --recompute | tail -1)

if [[ $output =~ [0-9] ]];
then
	echo "[success] run_solvers --parallel --recompute test succeeded"
else
	echo "[failure] run_solvers --parallel --recompute test failed with output:"
	echo $output
fi

# Run solvers with verifier
output=$(Commands/run_solvers.py --settings-file sparkle_test_settings_path --parallel --recompute --verifier SAT | tail -1)

if [[ $output =~ [0-9] ]];
then
	echo "[success] run_solvers --parallel --recompute --verifier SAT test succeeded"
else
	echo "[failure] run_solvers --parallel --recompute --verifier SAT test failed with output:"
	echo $output
fi

# Restore original settings
mv $default_settings_tmp $default_settings_path

