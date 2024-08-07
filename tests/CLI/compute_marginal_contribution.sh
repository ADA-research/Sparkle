#!/bin/bash

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/compute_marginal_contribution.sh
#SBATCH --output=Tmp/compute_marginal_contribution.sh.txt
#SBATCH --error=Tmp/compute_marginal_contribution.sh.err
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

# Prepare for test
settings_file="tests/CLI/test_files/Settings/sparkle_settings.ini"
instances_path="Examples/Resources/Instances/PTN"
extractor_path="Examples/Resources/Extractors/SAT-features-competition2012_revised_without_SatELite_sparkle"
solverA_path="Examples/Resources/Solvers/CSCCSat/"
solverB_path="Examples/Resources/Solvers/MiniSAT/"

sparkle/CLI/initialise.py > /dev/null
sparkle/CLI/add_instances.py $instances_path > /dev/null
sparkle/CLI/add_feature_extractor.py $extractor_path > /dev/null
sparkle/CLI/add_solver.py $solverA_path > /dev/null
sparkle/CLI/add_solver.py $solverB_path > /dev/null

# Activate test data to simulate the compute_features, run_solvers and construct_portfolio_selector commands
cp $feature_data_test $feature_data_path
cp $performance_data_test $performance_data_path

# Compute marginal contribution for the perfect selector
output_true="Marginal contribution (perfect selector) computing done!"
output=$(sparkle/CLI/compute_marginal_contribution.py --perfect --settings-file $settings_file | tail -1)

if [[ $output == $output_true ]];
then
	echo "[success] compute_marginal_contribution for the perfect selector test succeeded"
else
	echo "[failure] compute_marginal_contribution for the perfect selector test failed with output:"
	echo $output
fi
