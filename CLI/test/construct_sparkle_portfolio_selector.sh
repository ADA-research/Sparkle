#!/bin/bash

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/construct_sparkle_portfolio_selector.sh
#SBATCH --output=Tmp/construct_sparkle_portfolio_selector.sh.txt
#SBATCH --error=Tmp/construct_sparkle_portfolio_selector.sh.err
#SBATCH --partition=graceADA
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1

## Data
feature_data_path="Feature_Data/sparkle_feature_data.csv"
feature_data_tmp="CLI/test/test_files/Feature_Data/sparkle_feature_data.csv.tmp"
feature_data_test="CLI/test/test_files/Feature_Data/test_construct_sparkle_portfolio_selector.csv"

performance_data_path="Performance_Data/sparkle_performance_data.csv"
performance_data_tmp="CLI/test/test_files/Performance_Data/sparkle_performance_data.csv.tmp"
performance_data_test="CLI/test/test_files/Performance_Data/test_construct_sparkle_portfolio_selector.csv"

# Save user data if any
mv $feature_data_path $feature_data_tmp 2> /dev/null
mv $performance_data_path $performance_data_tmp 2> /dev/null

# Prepare for test
instances_path="Examples/Resources/Instances/PTN"
extractor_path="Examples/Resources/Extractors/SAT-features-competition2012_revised_without_SatELite_sparkle"
solverA_path="Examples/Resources/Solvers/CSCCSat/"
solverB_path="Examples/Resources/Solvers/MiniSAT/"

CLI/initialise.py > /dev/null
CLI/add_instances.py $instances_path > /dev/null
CLI/add_feature_extractor.py $extractor_path > /dev/null
CLI/add_solver.py --deterministic False $solverA_path > /dev/null
CLI/add_solver.py --deterministic False $solverB_path > /dev/null

# Activate test data to simulate the compute_features and run_solvers commands
cp $feature_data_test $feature_data_path
cp $performance_data_test $performance_data_path

# Construct sparkle portfolio selector
output_true="Marginal contribution (actual selector) computing done!"
output=$(CLI/construct_sparkle_portfolio_selector.py | tail -1)

if [[ $output == $output_true ]];
then
	echo "[success] construct_sparkle_portfolio_selector test succeeded"
else              
	echo "[failure] construct_sparkle_portfolio_selector test failed with output:"
	echo $output
fi

# Restore original data if any
mv $feature_data_tmp $feature_data_path 2> /dev/null
# OR true to get success exit code even when no user data was stored in the tmp file
mv $performance_data_tmp $performance_data_path 2> /dev/null || true

