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
feature_data_path="Feature_Data/sparkle_feature_data.csv"
feature_data_tmp="CLI/test/test_files/Feature_Data/sparkle_feature_data.csv.tmp"
feature_data_test="CLI/test/test_files/Feature_Data/test_construct_sparkle_portfolio_selector.csv"

performance_data_path="Performance_Data/sparkle_performance_data.csv"
performance_data_tmp="CLI/test/test_files/Performance_Data/sparkle_performance_data.csv.tmp"
performance_data_test="CLI/test/test_files/Performance_Data/test_construct_sparkle_portfolio_selector.csv"

selector_path="Sparkle_Portfolio_Selector/sparkle_portfolio_selector__@@SPARKLE@@__"
selector_tmp="CLI/test/test_files/Sparkle_Portfolio_Selector/sparkle_portfolio_selector__@@SPARKLE@@__.tmp"
selector_test="CLI/test/test_files/Sparkle_Portfolio_Selector/sparkle_portfolio_selector__@@SPARKLE@@__"

# Save user data if any
mv $feature_data_path $feature_data_tmp 2> /dev/null
mv $performance_data_path $performance_data_tmp 2> /dev/null
mv $selector_path $selector_tmp 2> /dev/null

# Prepare for test
instances_path="Examples/Resources/Instances/PTN"
extractor_path="Examples/Resources/Extractors/SAT-features-competition2012_revised_without_SatELite_sparkle"
solverA_path="Examples/Resources/Solvers/CSCCSat/"
solverB_path="Examples/Resources/Solvers/MiniSAT/"

CLI/initialise.py > /dev/null
CLI/add_instances.py $instances_path > /dev/null
CLI/add_feature_extractor.py $extractor_path > /dev/null
CLI/add_solver.py --deterministic 0 $solverA_path > /dev/null
CLI/add_solver.py --deterministic 0 $solverB_path > /dev/null

# Activate test data to simulate the compute_features, run_solvers and construct_sparkle_portfolio_selector commands
cp $feature_data_test $feature_data_path
cp $performance_data_test $performance_data_path
cp $selector_test $selector_path

# Generate report
output_true="Report generated ..."
output=$(CLI/generate_report.py --selection | tail -1)

if [[ $output == $output_true ]];
then
	echo "[success] generate_report test succeeded"
else              
	echo "[failure] generate_report test failed with output:"
	echo $output
fi

# Restore original data if any
mv $feature_data_tmp $feature_data_path 2> /dev/null
mv $performance_data_tmp $performance_data_path 2> /dev/null
# OR true to get success exit code even when no user data was stored in the tmp file
mv $selector_tmp $selector_path 2> /dev/null || true

