#!/bin/bash

# Import utils
. tests/CLI/utils.sh

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/construct_sparkle_portfolio_selector.sh
#SBATCH --output=Tmp/construct_sparkle_portfolio_selector.sh.txt
#SBATCH --error=Tmp/construct_sparkle_portfolio_selector.sh.err
#SBATCH --partition=graceADA
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1

slurm_true="slurm"
slurm_available=$(detect_slurm)

## Data
feature_data_path="Output/Feature_Data/sparkle_feature_data.csv"
feature_data_test="tests/CLI/test_files/Feature_Data/test_construct_sparkle_portfolio_selector.csv"

performance_data_path="Output/Performance_Data/sparkle_performance_data.csv"
performance_data_test="tests/CLI/test_files/Performance_Data/test_construct_sparkle_portfolio_selector.csv"

# Prepare for test
instances_path="Examples/Resources/Instances/PTN"
extractor_path="Examples/Resources/Extractors/SAT-features-competition2012_revised_without_SatELite_sparkle"
solverA_path="Examples/Resources/Solvers/CSCCSat/"
solverB_path="Examples/Resources/Solvers/MiniSAT/"

sparkle/CLI/initialise.py > /dev/null
sparkle/CLI/add_instances.py $instances_path > /dev/null
sparkle/CLI/add_feature_extractor.py $extractor_path > /dev/null
sparkle/CLI/add_solver.py $solverA_path > /dev/null
sparkle/CLI/add_solver.py $solverB_path > /dev/null

# Activate test data to simulate the compute_features and run_solvers commands
cp $feature_data_test $feature_data_path
cp $performance_data_test $performance_data_path

# Construct sparkle portfolio selector
output_true="Selector marginal contribution computing done!"
if [[ $slurm_available =~ "${slurm_true}" ]];
then
	output_true="Running selector construction. Waiting for Slurm job(s) with id(s): "
fi

output=$(sparkle/CLI/construct_sparkle_portfolio_selector.py | tail -1)

if [[ $output =~ "${output_true}" ]];
then
	echo "[success] construct_sparkle_portfolio_selector test succeeded"
	if [[ $slurm_available =~ "${slurm_true}" ]];
	then
        jobids=${output#"$output_true"}
        jobids=${jobids//,}
		scancel $jobids
	fi
else              
	echo "[failure] construct_sparkle_portfolio_selector test failed with output:"
	echo $output
    if [[ $slurm_available =~ "${slurm_true}" ]];
	then
		kill_started_jobs_slurm
	fi
fi

# TODO: Cancel the slurm job

# Restore original data if any
mv $feature_data_tmp $feature_data_path 2> /dev/null
# OR true to get success exit code even when no user data was stored in the tmp file
mv $performance_data_tmp $performance_data_path 2> /dev/null || true

