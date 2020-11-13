#!/bin/bash

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/construct_sparkle_portfolio_selector.sh
#SBATCH --output=TMP/construct_sparkle_portfolio_selector.sh.txt
#SBATCH --error=TMP/construct_sparkle_portfolio_selector.sh.err
#SBATCH --partition=graceADA
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1

## Data
feature_data_path="Feature_Data/sparkle_feature_data.csv"
feature_data_tmp="Commands/test/test_files/Feature_Data/sparkle_feature_data.csv.tmp"
feature_data_test="Commands/test/test_files/Feature_Data/test_construct_sparkle_portfolio_selector.csv"

performance_data_path="Performance_Data/sparkle_performance_data.csv"
performance_data_tmp="Commands/test/test_files/Performance_Data/sparkle_performance_data.csv.tmp"
performance_data_test="Commands/test/test_files/Performance_Data/test_construct_sparkle_portfolio_selector.csv"

cutoff_time_path="Performance_Data/sparkle_performance_data_cutoff_time_information.txt"
cutoff_time_tmp="Commands/test/test_files/Performance_Data/sparkle_performance_data_cutoff_time_information.txt.tmp"
cutoff_time_test="Commands/test/test_files/Performance_Data/test_construct_sparkle_portfolio_selector_cutoff_time.txt"

# Save user data if any
mv $feature_data_path $feature_data_tmp 2> /dev/null
mv $performance_data_path $performance_data_tmp 2> /dev/null
mv $cutoff_time_path $cutoff_time_tmp 2> /dev/null

# Prepare for test
instances_path="Examples/Resources/Instances/PTN"
extractor_path="Examples/Resources/Extractors/SAT-features-competition2012_revised_without_SatELite_sparkle"
solverA_path="Examples/Resources/Solvers/CSCCSat/"
solverB_path="Examples/Resources/Solvers/Lingeling/"

Commands/initialise.py > /dev/null
Commands/add_instances.py --run-solver-later --run-extractor-later $instances_path > /dev/null
Commands/add_feature_extractor.py --run-extractor-later $extractor_path > /dev/null
Commands/add_solver.py --run-solver-later --deterministic 0 $solverA_path > /dev/null
Commands/add_solver.py --run-solver-later --deterministic 0 $solverB_path > /dev/null

# Activate test data to simulate the compute_features and run_solvers commands
cp $feature_data_test $feature_data_path
cp $performance_data_test $performance_data_path
cp $cutoff_time_test $cutoff_time_path

# Construct sparkle portfolio selector
output_true="c Marginal contribution (actual selector) computing done!"
output=$(Commands/construct_sparkle_portfolio_selector.py | tail -1)

if [[ $output == $output_true ]];
then
	echo "[success] construct_sparkle_portfolio_selector test succeeded"
else              
	echo "[failure] construct_sparkle_portfolio_selector test failed with output:"
	echo $output
fi

# Restore original data if any
mv $feature_data_tmp $feature_data_path 2> /dev/null
mv $performance_data_tmp $performance_data_path 2> /dev/null
# OR true to get success exit code even when no user data was stored in the tmp file
mv $cutoff_time_tmp $cutoff_time_path 2> /dev/null || true

