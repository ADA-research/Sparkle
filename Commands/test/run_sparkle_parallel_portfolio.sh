#!/bin/bash

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/run_sparkle_parallel_portfolio.sh
#SBATCH --output=Tmp/run_sparkle_parallel_portfolio.sh.txt
#SBATCH --error=Tmp/run_sparkle_parallel_portfolio.sh.err
#SBATCH --partition=graceADA
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1

# Prepare for test
instances_path="Examples/Resources/Instances/PTN2/"
instance_path="${instances_path}Ptn-7824-b20.cnf"
extractor_path="Examples/Resources/Extractors/SAT-features-competition2012_revised_without_SatELite_sparkle"
solverA_path="Examples/Resources/Solvers/CSCCSat/"
solverB_path="Examples/Resources/Solvers/MiniSAT/"
solverC_path="Examples/Resources/Solvers/PbO-CCSAT-Generic/"

sparkle_test_settings_path="Commands/test/test_files/sparkle_settings.ini"

Commands/initialise.py > /dev/null
Commands/add_instances.py $instances_path > /dev/null
Commands/add_solver.py --deterministic 0 $solverA_path > /dev/null
Commands/add_solver.py --deterministic 0 $solverB_path > /dev/null
Commands/add_solver.py --deterministic 0 $solverC_path > /dev/null
Commands/construct_sparkle_parallel_portfolio.py > /dev/null

# Run sparkle parallel portfolio on a single instance
output_true="c Running Sparkle parallel portfolio is done!"
output=$(Commands/run_sparkle_parallel_portfolio.py --settings-file $sparkle_test_settings_path --instance-paths $instance_path | tail -1)

if [[ $output == $output_true ]];
then
	echo "[success] run_sparkle_parallel_portfolio test on a single instance succeeded"
else              
	echo "[failure] run_sparkle_parallel_portfolio test on a single instance failed with output:"
	echo $output
fi

# Run sparkle parallel portfolio on a set of instances
output=$(Commands/run_sparkle_parallel_portfolio.py --settings-file $sparkle_test_settings_path --instance-paths $instances_path | tail -1)

if [[ $output == $output_true ]];
then
	echo "[success] run_sparkle_parallel_portfolio test on a set of instances succeeded"
else              
	echo "[failure] run_sparkle_parallel_portfolio test on a set of instances failed with output:"
	echo $output
fi
