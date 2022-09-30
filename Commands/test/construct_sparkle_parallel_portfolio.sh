#!/bin/bash

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/construct_sparkle_parallel_portfolio.sh
#SBATCH --output=Tmp/construct_sparkle_parallel_portfolio.sh.txt
#SBATCH --error=Tmp/construct_sparkle_parallel_portfolio.sh.err
#SBATCH --partition=graceADA
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1

# Prepare for test
instances_path="Examples/Resources/Instances/PTN"
extractor_path="Examples/Resources/Extractors/SAT-features-competition2012_revised_without_SatELite_sparkle"
solverA_path="Examples/Resources/Solvers/CSCCSat/"
solverB_path="Examples/Resources/Solvers/MiniSAT/"
solverC_path="Examples/Resources/Solvers/PbO-CCSAT-Generic/"

Commands/initialise.py > /dev/null
Commands/add_instances.py $instances_path > /dev/null
Commands/add_solver.py --deterministic 0 $solverA_path > /dev/null
Commands/add_solver.py --deterministic 0 $solverB_path > /dev/null
Commands/add_solver.py --deterministic 0 $solverC_path > /dev/null

# Construct sparkle parallel portfolio
output_true="Sparkle parallel portfolio construction done!"
output=$(Commands/construct_sparkle_parallel_portfolio.py | tail -1)

if [[ $output == $output_true ]];
then
	echo "[success] construct_sparkle_parallel_portfolio test succeeded"
else              
	echo "[failure] construct_sparkle_parallel_portfolio test failed with output:"
	echo $output
fi
