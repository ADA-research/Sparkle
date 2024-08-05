#!/bin/bash

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/generate_report.sh
#SBATCH --output=Tmp/generate_report.sh.txt
#SBATCH --error=Tmp/generate_report.sh.err
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

selector_path="Output/Selection/sparkle_portfolio_selector"
selector_test="tests/CLI/test_files/Sparkle_Portfolio_Selector/sparkle_portfolio_selector"

# Prepare for test
instances_path="Examples/Resources/Instances/PTN"
extractor_path="Examples/Resources/Extractors/SAT-features-competition2012_revised_without_SatELite_sparkle"
solverA_path="Examples/Resources/Solvers/CSCCSat/"
solverB_path="Examples/Resources/Solvers/MiniSAT/"
sparkle_settings_path="tests/CLI/test_files/Settings/sparkle_settings.ini"

sparkle/CLI/initialise.py > /dev/null
sparkle/CLI/add_instances.py $instances_path > /dev/null
sparkle/CLI/add_feature_extractor.py $extractor_path > /dev/null
sparkle/CLI/add_solver.py $solverA_path > /dev/null
sparkle/CLI/add_solver.py $solverB_path > /dev/null

# Activate test data to simulate the compute_features, run_solvers and construct_portfolio_selector commands
cp $feature_data_test $feature_data_path
cp $performance_data_test $performance_data_path
cp $selector_test $selector_path

# Generate report
output_true="Report generated ..."
output=$(sparkle/CLI/generate_report.py --selection --settings-file $sparkle_settings_path | tail -1)

if [[ $output == $output_true ]];
then
	echo "[success] generate_report test succeeded"
else              
	echo "[failure] generate_report test failed with output:"
	echo $output
fi
