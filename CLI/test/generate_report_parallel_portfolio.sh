#!/bin/bash

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/generate_report_parallel_portfolio.sh
#SBATCH --output=Tmp/generate_report_parallel_portfolio.sh.txt
#SBATCH --error=Tmp/generate_report_parallel_portfolio.sh.err
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

sparkle_test_settings_path="CLI/test/test_files/sparkle_settings.ini"

CLI/initialise.py > /dev/null
CLI/add_instances.py $instances_path > /dev/null
CLI/add_solver.py --deterministic False $solverA_path > /dev/null
CLI/add_solver.py --deterministic False $solverB_path > /dev/null
CLI/add_solver.py --deterministic False $solverC_path > /dev/null
CLI/run_parallel_portfolio.py --settings-file $sparkle_test_settings_path --instance-paths $instance_path > /dev/null

# Generate report for parallel portfolio on a single instance
output_true="Parallel portfolio report generated ..."
output=$(CLI/generate_report.py --settings-file $sparkle_test_settings_path | tail -1)

if [[ $output == $output_true ]];
then
	echo "[success] generate report for parallel portfolio test on a single instance succeeded"
else              
	echo "[failure] generate report for parallel portfolio test on a single instance failed with output:"
	echo $output
fi
