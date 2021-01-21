#!/bin/bash

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/generate_report_for_test.sh
#SBATCH --output=TMP/generate_report_for_test.sh.txt
#SBATCH --error=TMP/generate_report_for_test.sh.err
#SBATCH --partition=graceADA
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1

## Data
selector_path="Sparkle_Portfolio_Selector/sparkle_portfolio_selector__@@SPARKLE@@__"
selector_tmp="Commands/test/test_files/Sparkle_Portfolio_Selector/sparkle_portfolio_selector__@@SPARKLE@@__.tmp"
selector_test="Commands/test/test_files/Sparkle_Portfolio_Selector/sparkle_portfolio_selector__@@SPARKLE@@__"

test_results_dir="Test_Cases/PTN2/"
test_results_path="Test_Cases/PTN2/sparkle_performance_data.csv"
test_results_tmp="Test_Cases/PTN2/sparkle_performance_data.tmp"
test_results_test="Commands/test/test_files/Test_Cases/"

# Save user data if any
mv $selector_path $selector_tmp 2> /dev/null
mv $test_results_path $test_results_tmp 2> /dev/null

# Prepare for test
instances_path="Examples/Resources/Instances/PTN"
instances_path_test="Examples/Resources/Instances/PTN2"
instance_path_test="Examples/Resources/Instances/PTN2/Ptn-7824-b20.cnf"
extractor_path="Examples/Resources/Extractors/SAT-features-competition2012_revised_without_SatELite_sparkle"
solverA_path="Examples/Resources/Solvers/CSCCSat/"
solverB_path="Examples/Resources/Solvers/Lingeling/"

sparkle_test_settings_path="Commands/test/test_files/sparkle_settings.ini"

Commands/initialise.py > /dev/null
Commands/add_instances.py --run-solver-later --run-extractor-later $instances_path > /dev/null
Commands/add_feature_extractor.py --run-extractor-later $extractor_path > /dev/null
Commands/add_solver.py --run-solver-later --deterministic 0 $solverA_path > /dev/null
Commands/add_solver.py --run-solver-later --deterministic 0 $solverB_path > /dev/null

# Activate test data to simulate the compute_features, run_solvers, construct_sparkle_portfolio_selector and run_sparkle_portfolio_selector commands
cp $selector_test $selector_path
cp -r $test_results_test ./

# Run generate report for tetst
output_true="c Report for test generated ..."
output=$(Commands/generate_report_for_test.py $test_results_dir | tail -1)
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
mv $test_results_tmp $test_results_path 2> /dev/null
mv $selector_tmp $selector_path 2> /dev/null || true
