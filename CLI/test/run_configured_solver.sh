#!/bin/bash

# Import utils
. CLI/test/utils.sh

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/run_configured_solver.sh
#SBATCH --output=Tmp/run_configured_solver.sh.txt
#SBATCH --error=Tmp/run_configured_solver.sh.err
#SBATCH --partition=graceADA
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1

CLI/initialise.py > /dev/null

# Copy configuration results and other files to simulate the configuration command
configuration_results_path="CLI/test/test_files/results"
configuration_files_path="CLI/test/test_files/PbO-CCSAT-Generic_PTN/PTN_train.txt"
smac_path="Components/smac-v2.10.03-master-778/"
smac_configuration_files_path="$smac_path/scenarios/PbO-CCSAT-Generic/"
# TODO: Save possibly existing results directory
cp -r $configuration_results_path $smac_path
mkdir -p $smac_configuration_files_path # Make sure directory exists
cp $configuration_files_path $smac_configuration_files_path

#Check if Slurm is present in the env
slurm_true="slurm"
slurm_available=$(detect_slurm)

# Copy scenario
scenario_path="Output/latest_scenario.ini"
scenario_tmp="Output/latest_scenario.tmp"
scenario_test="CLI/test/test_files/Output/latest_scenario.ini"
mv $scenario_path $scenario_tmp 2> /dev/null # Save user scenario
cp $scenario_test $scenario_path # Activate test scenario

# Slurm settings
slurm_settings_path="Settings/sparkle_slurm_settings.txt"
slurm_settings_tmp="Settings/sparkle_slurm_settings.tmp"
slurm_settings_test="CLI/test/test_files/sparkle_slurm_settings.txt"
mv $slurm_settings_path $slurm_settings_tmp # Save user settings
cp $slurm_settings_test $slurm_settings_path # Activate test settings

sparkle_test_settings_path="CLI/test/test_files/sparkle_settings.ini"

# Instance and solver paths
instances_path_test="Examples/Resources/Instances/PTN2"
instance_path_test="Examples/Resources/Instances/PTN2/Ptn-7824-b20.cnf"
solver_path="Examples/Resources/Solvers/PbO-CCSAT-Generic/"

# Run commands to prepare Sparkle for the test

CLI/add_solver.py --deterministic 0 $solver_path > /dev/null

# Run configured solver on a single instance
output_true="Running configured solver done!"
output=$(CLI/run_configured_solver.py $instance_path_test --settings-file $sparkle_test_settings_path --run-on $slurm_available | tail -1)

if [[ $output == $output_true ]];
then
	echo "[success] ($slurm_available) run_configured_solver on single instance test succeeded"
else              
	echo "[failure] ($slurm_available) run_configured_solver on single instance test failed with output:"
	echo $output
fi

# Run configured solver on an instance directory
if [[ $slurm_available == $slurm_true ]];
then
	output_true="Running configured solver in parallel. Waiting for Slurm job(s) with id(s):"
fi
output=$(CLI/run_configured_solver.py $instances_path_test --settings-file $sparkle_test_settings_path --parallel --run-on $slurm_available | tail -1)

if [[ $output =~ "${output_true}" ]];
then
	echo "[success] ($slurm_available) run_configured_solver in parallel on instance directory test succeeded"
else              
	echo "[failure] ($slurm_available) run_configured_solver in parallel on instance directory test failed with output:"
	echo $output
fi

# Restore original scenario if any
# OR true to get success exit code even when no user data was stored in the tmp file
mv $scenario_tmp $scenario_path 2> /dev/null || true

# Restore original settings
mv $slurm_settings_tmp $slurm_settings_path
