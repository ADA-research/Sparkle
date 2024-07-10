#!/bin/bash -u

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/generate_report_for_configuration.sh
#SBATCH --output=Tmp/generate_report_for_configuration.sh.txt
#SBATCH --error=Tmp/generate_report_for_configuration.sh.err
#SBATCH --partition=Test
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1

# Settings
sparkle_test_settings_path="CLI/test/test_files/sparkle_settings.ini"

# Prepare for test
examples_path="Examples/Resources/"
instances_path_train="Instances/PTN/"
instances_path_test="Instances/PTN2/"
solver_path="Solvers/PbO-CCSAT-Generic/"
instances_src_path_train="${examples_path}${instances_path_train}"
instances_src_path_test="${examples_path}${instances_path_test}"
solver_src_path="${examples_path}${solver_path}"

scenario_path="Output/latest_scenario.ini"
scenario_tmp="${scenario_path}_tmp"
scenario_test="CLI/test/test_files/latest_scenario.ini"

config_scenario_path="Output/Configuration/Raw_Data/SMAC2/scenarios/"
validation_scenario_path="Output/Validation/"
config_test_data="CLI/test/test_files/Output/Configuration/Raw_Data/SMAC2/scenarios/PbO-CCSAT-Generic_PTN"
validation_train_data="CLI/test/test_files/Output/Validation/PbO-CCSAT-Generic_PTN/"
validation_test_data="CLI/test/test_files/Output/Validation/PbO-CCSAT-Generic_PTN2/"

CLI/initialise.py > /dev/null
CLI/add_instances.py $instances_src_path_train > /dev/null
CLI/add_instances.py $instances_src_path_test > /dev/null
CLI/add_solver.py $solver_src_path > /dev/null

# Copy scenario to simulate configuration
mv $scenario_path $scenario_tmp 2> /dev/null # Save user data (if any)
cp $scenario_test $scenario_path

# Prepare configuration scenario output files
mkdir -p $config_scenario_path # Make sure directory exists
mkdir -p $validation_scenario_path
cp -r $config_test_data $config_scenario_path
cp -r $validation_train_data $validation_scenario_path
cp -r $validation_test_data $validation_scenario_path

# Test generate report for configuration with both train and test sets
output_true="Report is placed at:"
output=$(CLI/generate_report.py --solver $solver_path --instance-set-train $instances_path_train --instance-set-test $instances_path_test --settings-file $sparkle_test_settings_path | tail -1)

if [[ $output == $output_true* ]];
then
	echo "[success] generate_report_for_configuration with both train and test sets test succeeded"
else              
	echo "[failure] generate_report_for_configuration with both train and test sets test failed with output:"
	echo $output
fi

# Test generate report for configuration with just training set
output=$(CLI/generate_report.py --solver $solver_path --instance-set-train $instances_path_train --settings-file $sparkle_test_settings_path | tail -1)

if [[ $output == $output_true* ]];
then
	echo "[success] generate_report_for_configuration with just training set test succeeded"
else
	echo "[failure] generate_report_for_configuration with just training set test failed with output:"
	echo $output
fi

# Remove copied data
rm -rf $config_scenario_path
rm -rf $validation_scenario_path

# Restore original data if any
# OR true to get success exit code even when no user data was stored in the tmp file
mv $scenario_tmp $scenario_path 2> /dev/null || true
