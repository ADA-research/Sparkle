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

# Activate environment
source activate sparkle_test &> /dev/null

# Prepare for test
instances_path="Examples/Resources/Instances/SAT_test"
extractor_path="Examples/Resources/Extractors/SAT-features-competition2012_revised_without_SatELite_sparkle"
solverA_path="Examples/Resources/Solvers/CSCCSat/"
solverB_path="Examples/Resources/Solvers/Lingeling/"

Commands/initialise.py > /dev/null
Commands/add_instances.py --run-solver-later --run-extractor-later $instances_path > /dev/null
Commands/add_feature_extractor.py --run-extractor-later $extractor_path > /dev/null
Commands/add_solver.py --run-solver-later --deterministic 0 $solverA_path > /dev/null
Commands/add_solver.py --run-solver-later --deterministic 0 $solverB_path > /dev/null
Commands/compute_features.py > /dev/null
dependency=$(Commands/run_solvers.py -parallel | tail -1)

# Wait for the dependency to be done
while [[ $(squeue -j $dependency) =~ [0-9] ]]; do
	sleep 1
done

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

