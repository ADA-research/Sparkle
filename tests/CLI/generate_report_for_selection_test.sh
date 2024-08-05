#!/bin/bash

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/generate_report_for_selection_test.sh
#SBATCH --output=Tmp/generate_report_for_selection_test.sh.txt
#SBATCH --error=Tmp/generate_report_for_selection_test.sh.err
#SBATCH --partition=graceADA
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1

## Data
feature_data_path="Output/Feature_Data/sparkle_feature_data.csv"
feature_data_test="tests/CLI/test_files/Feature_Data/test_construct_portfolio_selector.csv"

performance_data_path="Output/Performance_Data/sparkle_performance_data.csv"
performance_data_test="tests/CLI/test_files/Performance_Data/test_construct_portfolio_selector.csv"

# Copy selector construction output to simulate the construct_portfolio_selector command
source_output="tests/CLI/test_files/Output/Selection"
target_output="Output"
instances_path="Examples/Resources/Instances/PTN"
instances_path_test="Examples/Resources/Instances/PTN2"
instance_path_test="Examples/Resources/Instances/PTN2/Ptn-7824-b20.cnf"
extractor_path="Examples/Resources/Extractors/SAT-features-competition2012_revised_without_SatELite_sparkle"
solverA_path="Examples/Resources/Solvers/CSCCSat/"
solverB_path="Examples/Resources/Solvers/MiniSAT/"

scenario_source="tests/CLI/test_files/Settings/latest_scenario_selection.ini"
scenario_path="Output/latest_scenario.ini"

sparkle_test_settings_path="tests/CLI/test_files/Settings/sparkle_settings.ini"

sparkle/CLI/initialise.py > /dev/null
sparkle/CLI/add_instances.py $instances_path > /dev/null
sparkle/CLI/add_feature_extractor.py $extractor_path > /dev/null
sparkle/CLI/add_solver.py $solverA_path > /dev/null
sparkle/CLI/add_solver.py $solverB_path > /dev/null

# Activate test data to simulate the compute_features, run_solvers, construct_portfolio_selector and run_portfolio_selector commands
cp $feature_data_test $feature_data_path
cp $performance_data_test $performance_data_path
cp $scenario_source $scenario_path
cp -r $source_output $target_output

# Run generate report for tetst
output_true="Report for test generated ..."
output=$(sparkle/CLI/generate_report.py --settings-file $sparkle_test_settings_path | tail -1)
# --settings-file $sparkle_test_settings_path

if [[ $output == $output_true ]];
then
	echo "[success] generate_report_for_selection_test test succeeded"
else
	echo "[failure] generate_report_for_selection_test test failed with output:"
	echo $output
fi
