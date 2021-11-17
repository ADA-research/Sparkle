#!/bin/bash

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/generate_report_for_configuration.sh
#SBATCH --output=Tmp/generate_report_for_configuration.sh.txt
#SBATCH --error=Tmp/generate_report_for_configuration.sh.err
#SBATCH --partition=graceADA
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1

# Settings
slurm_settings_path="Settings/sparkle_slurm_settings.txt"
slurm_settings_tmp="Settings/sparkle_slurm_settings.tmp"
slurm_settings_test="Commands/test/test_files/sparkle_slurm_settings.txt"
mv $slurm_settings_path $slurm_settings_tmp # Save user settings
cp $slurm_settings_test $slurm_settings_path # Activate test settings

sparkle_test_settings_path="Commands/test/test_files/sparkle_settings.ini"

# Prepare for test
examples_path="Examples/Resources/"
instances_path_train="Instances/PTN/"
instances_path_test="Instances/PTN2/"
solver_path="Solvers/PbO-CCSAT-Generic/"
instances_src_path_train="${examples_path}${instances_path_train}"
instances_src_path_test="${examples_path}${instances_path_test}"
solver_src_path="${examples_path}${solver_path}"

configuration_results_path="Commands/test/test_files/results/"
validation_results_path="Commands/test/test_files/PbO-CCSAT-Generic/"
smac_path="Components/smac-v2.10.03-master-778/"
smac_validation_results_path="$smac_path/example_scenarios/"

Commands/initialise.py > /dev/null
Commands/add_instances.py $instances_src_path_train > /dev/null
Commands/add_instances.py $instances_src_path_test > /dev/null
Commands/add_solver.py --deterministic 0 $solver_src_path > /dev/null

# Copy configuration results to simulate the configuration command
cp -r $configuration_results_path $smac_path
# Copy validation results to simulate the validation command
mkdir -p $smac_validation_results_path # Make sure directory exists
cp -r $validation_results_path $smac_validation_results_path

# Test generate report for configuration with both train and test sets
output_true="c Generating report for configuration done!"
output=$(Commands/generate_report.py --solver $solver_path --instance-set-train $instances_path_train --instance-set-test $instances_path_test --settings-file $sparkle_test_settings_path | tail -1)

if [[ $output == $output_true ]];
then
	echo "[success] generate_report_for_configuration with both train and test sets test succeeded"
else              
	echo "[failure] generate_report_for_configuration with both train and test sets test failed with output:"
	echo $output
fi

# Test generate report for configuration with just training set
output=$(Commands/generate_report.py --solver $solver_path --instance-set-train $instances_path_train --settings-file $sparkle_test_settings_path | tail -1)

if [[ $output == $output_true ]];
then
	echo "[success] generate_report_for_configuration with just training set test succeeded"
else
	echo "[failure] generate_report_for_configuration with just training set test failed with output:"
	echo $output
fi

# Restore original settings
mv $slurm_settings_tmp $slurm_settings_path

