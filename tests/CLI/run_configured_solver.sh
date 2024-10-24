#!/bin/bash

# Import utils
. tests/CLI/utils.sh

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

sparkle/CLI/initialise.py > /dev/null

# Copy configuration results and other files to simulate the configuration command
config_scenario_path="Output/Configuration/Raw_Data/SMAC2/scenarios/"
config_test_data="tests/CLI/test_files/Output/Configuration/Raw_Data/SMAC2/scenarios/PbO-CCSAT-Generic_PTN"

mkdir -p $config_scenario_path # Make sure directory exists
cp -r $config_test_data $config_scenario_path

#Check if Slurm is present in the env
slurm_true="slurm"
slurm_available=$(detect_slurm)

# Copy scenario
scenario_path="Output/latest_scenario.ini"
scenario_test="tests/CLI/test_files/Settings/latest_scenario_configuration.ini"
cp $scenario_test $scenario_path # Activate test scenario

# Settings
sparkle_test_settings_path="tests/CLI/test_files/Settings/sparkle_settings.ini"

# Instance and solver paths
instances_path_train="Examples/Resources/Instances/PTN"
instances_path_test="Examples/Resources/Instances/PTN2"
instance_path_test="Examples/Resources/Instances/PTN2/Ptn-7824-b20.cnf"
solver_path="Examples/Resources/Solvers/PbO-CCSAT-Generic/"

# Run commands to prepare Sparkle for the test
sparkle/CLI/add_instances.py $instances_path_train > /dev/null
sparkle/CLI/add_solver.py $solver_path > /dev/null

# Run configured solver on a single instance
output_true="Running configured solver done!"
output=$(sparkle/CLI/run_configured_solver.py $instance_path_test --settings-file $sparkle_test_settings_path --run-on local | tail -1)

if [[ $output == $output_true ]];
then
	echo "[success] (local) run_configured_solver on single instance test succeeded"
else
	echo "[failure] (local) run_configured_solver on single instance test failed with output:"
	echo $output
fi

# Run configured solver on an instance directory
if [[ $slurm_available == $slurm_true ]];
then
	output_true="Running configured solver. Waiting for Slurm job(s) with id(s):"
fi
output=$(sparkle/CLI/run_configured_solver.py $instances_path_test --settings-file $sparkle_test_settings_path --run-on slurm | tail -1)

if [[ $output =~ "${output_true}" ]];
then
	echo "[success] (slurm) run_configured_solver on instance directory test succeeded"
else
	echo "[failure] (slurm) run_configured_solver on instance directory test failed with output:"
	echo $output
fi

# Restore original scenario if any
# OR true to get success exit code even when no user data was stored in the tmp file
mv $scenario_tmp $scenario_path 2> /dev/null || true

