#!/bin/bash

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/test_configured_solver_and_default_solver.sh
#SBATCH --output=TMP/test_configured_solver_and_default_solver.sh.txt
#SBATCH --error=TMP/test_configured_solver_and_default_solver.sh.err
#SBATCH --partition=graceADA
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1

# Activate environment
source activate sparkle_test &> /dev/null

# Settings
slurm_settings_path="Settings/sparkle_slurm_settings.txt"
slurm_settings_tmp="Settings/sparkle_slurm_settings.tmp"
mv $slurm_settings_path $slurm_settings_tmp # Save user settings
partition="graceADA"
exclude=""
mem="3000"
echo "--partition=$partition" > $slurm_settings_path
echo "--exclude=$exclude" >> $slurm_settings_path
echo "--mem-per-cpu=$mem" >> $slurm_settings_path

smac_settings_path="Settings/sparkle_smac_settings.txt"
smac_settings_tmp="Settings/sparkle_smac_settings.tmp"
mv $smac_settings_path $smac_settings_tmp # Save user settings
run_obj="RUNTIME"
time_budget="30" # 30 seconds
cutoff_time="5" # 5 seconds
cutoff_length="max"
runs="5"
runs_parallel=$runs
echo "smac_run_obj = $run_obj" > $smac_settings_path
echo "smac_whole_time_budget = $time_budget" >> $smac_settings_path
echo "smac_each_run_cutoff_time = $cutoff_time" >> $smac_settings_path
echo "smac_each_run_cutoff_length = $cutoff_length" >> $smac_settings_path
echo "num_of_smac_run = $runs" >> $smac_settings_path
echo "num_of_smac_run_in_parallel = $runs_parallel" >> $smac_settings_path

# Prepare for test
instances_path_train="Examples/Resources/Instances/PTN/"
instances_path_test="Examples/Resources/Instances/PTN2/"
solver_path="Examples/Resources/Solvers/PbO-CCSAT-Generic/"

Commands/initialise.py > /dev/null
Commands/add_instances.py --run-solver-later --run-extractor-later $instances_path_train > /dev/null
Commands/add_instances.py --run-solver-later --run-extractor-later $instances_path_test > /dev/null
Commands/add_solver.py --run-solver-later --deterministic 0 $solver_path > /dev/null
#Commands/configure_solver.py --solver $solver_path --instance-set-train $instances_path_train > /dev/null
dependency=$(Commands/configure_solver.py --solver $solver_path --instance-set-train $instances_path_train | tail -1)

# Wait for the dependency to be done
while [[ $(squeue -j $dependency) =~ [0-9] ]]; do
	sleep 1
done

# Test configured solver and default solver
output=$(Commands/test_configured_solver_and_default_solver.py --solver $solver_path --instance-set-train $instances_path_train --instance-set-test $instances_path_test | tail -1)

if [[ $output =~ [0-9] ]];
then
	echo "[success] test_configured_solver_and_default_solver test succeeded"
else              
	echo "[failure] test_configured_solver_and_default_solver test failed with output:"
	echo $output
fi

# Restore original settings
mv $slurm_settings_tmp $slurm_settings_path
mv $smac_settings_tmp $smac_settings_path

