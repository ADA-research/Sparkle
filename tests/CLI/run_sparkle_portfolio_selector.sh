#!/bin/bash

# Import utils
. tests/CLI/utils.sh

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/run_sparkle_portfolio_selector.sh
#SBATCH --output=Tmp/run_sparkle_portfolio_selector.sh.txt
#SBATCH --error=Tmp/run_sparkle_portfolio_selector.sh.err
#SBATCH --partition=graceADA
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1

## Data
selector_path="Sparkle_Portfolio_Selector/sparkle_portfolio_selector"
selector_tmp="tests/CLI/test_files/Sparkle_Portfolio_Selector/sparkle_portfolio_selector.tmp"
selector_test="tests/CLI/test_files/Sparkle_Portfolio_Selector/sparkle_portfolio_selector"

# Save user data if any
mv $selector_path $selector_tmp 2> /dev/null

# Prepare for test
instances_path="Examples/Resources/Instances/PTN"
instances_path_test="Examples/Resources/Instances/PTN2"
instance_path_test="Examples/Resources/Instances/PTN2/Ptn-7824-b20.cnf"
extractor_path="Examples/Resources/Extractors/SAT-features-competition2012_revised_without_SatELite_sparkle"
solverA_path="Examples/Resources/Solvers/CSCCSat/"
solverB_path="Examples/Resources/Solvers/MiniSAT/"

sparkle_test_settings_path="tests/CLI/test_files/Settings/sparkle_settings.ini"
slurm_true="slurm"
slurm_available=$(detect_slurm)

sparkle/CLI/initialise.py > /dev/null
sparkle/CLI/add_instances.py $instances_path > /dev/null
sparkle/CLI/add_feature_extractor.py $extractor_path > /dev/null
sparkle/CLI/add_solver.py $solverA_path > /dev/null
sparkle/CLI/add_solver.py $solverB_path > /dev/null

# Activate test data to simulate the compute_features, run_solvers and construct_sparkle_portfolio_selector commands
cp $selector_test $selector_path

# Run portfolio selector on a single instance
output_true="Running Sparkle portfolio selector done!"
output=$(sparkle/CLI/run_sparkle_portfolio_selector.py $instance_path_test --settings-file $sparkle_test_settings_path --run-on $slurm_available| tail -1)

if [[ $output == $output_true ]];
then
	echo "[success] ($slurm_available) run_sparkle_portfolio_selector on single instance test succeeded"
else
	echo "[failure] ($slurm_available) run_sparkle_portfolio_selector on single instance test failed with output:"
	echo $output
fi

# Run portfolio selector on an instance directory
if [[ $slurm_available == $slurm_true ]];
then
	output_true="Sparkle portfolio selector is running ..."
fi
output=$(sparkle/CLI/run_sparkle_portfolio_selector.py $instances_path_test --settings-file $sparkle_test_settings_path --run-on $slurm_available| tail -1)

if [[ $output == $output_true ]];
then
	echo "[success] ($slurm_available) run_sparkle_portfolio_selector on instance directory test succeeded"
else
	echo "[failure] ($slurm_available) run_sparkle_portfolio_selector on instance directory test failed with output:"
	echo $output
fi

# Restore original data if any
# OR true to get success exit code even when no user data was stored in the tmp file
mv $selector_tmp $selector_path 2> /dev/null || true

