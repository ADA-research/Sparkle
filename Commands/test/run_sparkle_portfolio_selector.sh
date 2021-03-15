#!/bin/bash

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/run_sparkle_portfolio_selector.sh
#SBATCH --output=TMP/run_sparkle_portfolio_selector.sh.txt
#SBATCH --error=TMP/run_sparkle_portfolio_selector.sh.err
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

# Save user data if any
mv $selector_path $selector_tmp 2> /dev/null

# Prepare for test
instances_path="Examples/Resources/Instances/PTN"
instances_path_test="Examples/Resources/Instances/PTN2"
instance_path_test="Examples/Resources/Instances/PTN2/Ptn-7824-b20.cnf"
extractor_path="Examples/Resources/Extractors/SAT-features-competition2012_revised_without_SatELite_sparkle"
solverA_path="Examples/Resources/Solvers/CSCCSat/"
solverB_path="Examples/Resources/Solvers/MiniSAT/"

sparkle_test_settings_path="Commands/test/test_files/sparkle_settings.ini"

Commands/initialise.py > /dev/null
Commands/add_instances.py --run-solver-later --run-extractor-later $instances_path > /dev/null
Commands/add_feature_extractor.py --run-extractor-later $extractor_path > /dev/null
Commands/add_solver.py --run-solver-later --deterministic 0 $solverA_path > /dev/null
Commands/add_solver.py --run-solver-later --deterministic 0 $solverB_path > /dev/null

# Activate test data to simulate the compute_features, run_solvers and construct_sparkle_portfolio_selector commands
cp $selector_test $selector_path

# Run portfolio selector on a single instance
output_true="c Running Sparkle portfolio selector done!"
output=$(Commands/run_sparkle_portfolio_selector.py $instance_path_test --settings-file $sparkle_test_settings_path | tail -1)

if [[ $output == $output_true ]];
then
	echo "[success] run_sparkle_portfolio_selector on single instance test succeeded"
else              
	echo "[failure] run_sparkle_portfolio_selector on single instance test failed with output:"
	echo $output
fi

# Run portfolio selector on an instance directory
output_true="c Sparkle portfolio selector is running ..."
output=$(Commands/run_sparkle_portfolio_selector.py $instances_path_test --settings-file $sparkle_test_settings_path | tail -1)

if [[ $output == $output_true ]];
then
	echo "[success] run_sparkle_portfolio_selector on instance directory test succeeded"
else              
	echo "[failure] run_sparkle_portfolio_selector on instance directory test failed with output:"
	echo $output
fi

# Restore original data if any
# OR true to get success exit code even when no user data was stored in the tmp file
mv $selector_tmp $selector_path 2> /dev/null || true

