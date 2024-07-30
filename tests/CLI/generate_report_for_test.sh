#!/bin/bash

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/generate_report_for_test.sh
#SBATCH --output=Tmp/generate_report_for_test.sh.txt
#SBATCH --error=Tmp/generate_report_for_test.sh.err
#SBATCH --partition=graceADA
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1

## Data
feature_data_path="Feature_Data/sparkle_feature_data.csv"
feature_data_tmp="tests/CLI/test_files/Feature_Data/sparkle_feature_data.csv.tmp"
feature_data_test="tests/CLI/test_files/Feature_Data/test_construct_sparkle_portfolio_selector.csv"

performance_data_path="Performance_Data/sparkle_performance_data.csv"
performance_data_tmp="tests/CLI/test_files/Performance_Data/sparkle_performance_data.csv.tmp"
performance_data_test="tests/CLI/test_files/Performance_Data/test_construct_sparkle_portfolio_selector.csv"

<<<<<<<< HEAD:tests/CLI/generate_report_for_selection_test.sh
selector_path="Output/Selection/sparkle_portfolio_selector"
selector_tmp="tests/CLI/test_files/Sparkle_Portfolio_Selector/sparkle_portfolio_selector.tmp"
selector_test="tests/CLI/test_files/Sparkle_Portfolio_Selector/sparkle_portfolio_selector"

test_results_dir="Output/Selection/Test_Cases/PTN2/"
test_results_path="Output/Selection/Test_Cases/PTN2/sparkle_performance_data.csv"
test_results_tmp="Output/Selection/Test_Cases/PTN2/sparkle_performance_data.tmp"
test_results_test="tests/CLI/test_files/Selector/Test_Cases/"
========
selector_path="Sparkle_Portfolio_Selector/sparkle_portfolio_selector"
selector_tmp="tests/CLI/test_files/Sparkle_Portfolio_Selector/sparkle_portfolio_selector.tmp"
selector_test="tests/CLI/test_files/Sparkle_Portfolio_Selector/sparkle_portfolio_selector"

test_results_dir="Test_Cases/PTN2/"
test_results_path="Test_Cases/PTN2/sparkle_performance_data.csv"
test_results_tmp="Test_Cases/PTN2/sparkle_performance_data.tmp"
test_results_test="tests/CLI/test_files/Test_Cases/"
>>>>>>>> b4a6ece2e94acc027435b9199c64863c5eb51e47:tests/CLI/generate_report_for_test.sh

# Save user data if any
mv $feature_data_path $feature_data_tmp 2> /dev/null
mv $performance_data_path $performance_data_tmp 2> /dev/null
mv $selector_path $selector_tmp 2> /dev/null
mv $test_results_path $test_results_tmp 2> /dev/null

# Prepare for test
instances_path="Examples/Resources/Instances/PTN"
instances_path_test="Examples/Resources/Instances/PTN2"
instance_path_test="Examples/Resources/Instances/PTN2/Ptn-7824-b20.cnf"
extractor_path="Examples/Resources/Extractors/SAT-features-competition2012_revised_without_SatELite_sparkle"
solverA_path="Examples/Resources/Solvers/CSCCSat/"
solverB_path="Examples/Resources/Solvers/MiniSAT/"

sparkle_test_settings_path="tests/CLI/test_files/Settings/sparkle_settings.ini"

sparkle/CLI/initialise.py > /dev/null
sparkle/CLI/add_instances.py $instances_path > /dev/null
sparkle/CLI/add_feature_extractor.py $extractor_path > /dev/null
sparkle/CLI/add_solver.py $solverA_path > /dev/null
sparkle/CLI/add_solver.py $solverB_path > /dev/null

# Activate test data to simulate the compute_features, run_solvers, construct_sparkle_portfolio_selector and run_sparkle_portfolio_selector commands
cp $feature_data_test $feature_data_path
cp $performance_data_test $performance_data_path
cp $selector_test $selector_path
cp -r $test_results_test ./

# Run generate report for tetst
output_true="Report for test generated ..."
output=$(sparkle/CLI/generate_report.py --test-case-directory $test_results_dir --settings-file $sparkle_test_settings_path | tail -1)
# --settings-file $sparkle_test_settings_path

if [[ $output == $output_true ]];
then
	echo "[success] generate_report_for_test test succeeded"
else
	echo "[failure] generate_report_for_test test failed with output:"
	echo $output
fi

# Restore original data if any
# OR true to get success exit code even when no user data was stored in the tmp file
mv $feature_data_tmp $feature_data_path 2> /dev/null
mv $performance_data_tmp $performance_data_path 2> /dev/null
mv $test_results_tmp $test_results_path 2> /dev/null
mv $selector_tmp $selector_path 2> /dev/null || true

