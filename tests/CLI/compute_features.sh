#!/bin/bash

# Import utils
. tests/CLI/utils.sh

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/compute_features.sh
#SBATCH --output=Tmp/compute_features.sh.txt
#SBATCH --error=Tmp/compute_features.sh.err
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1

# Settings
sparkle_test_settings_path="tests/CLI/test_files/Settings/sparkle_settings.ini"
slurm_true="slurm"
slurm_available=$(detect_slurm)

# Prepare for test
instances_path="Examples/Resources/Instances/PTN"
extractor_path="Examples/Resources/Extractors/SAT-features-competition2012_revised_without_SatELite_sparkle"

sparkle/CLI/initialise.py > /dev/null
sparkle/CLI/add_instances.py $instances_path > /dev/null
sparkle/CLI/add_feature_extractor.py $extractor_path > /dev/null


output_true="Running the extractors through Slurm"
output=$(sparkle/CLI/compute_features.py --settings-file $sparkle_test_settings_path --run-on slurm | tail -1)

if [[ $output =~ "${output_true}" ]];
then
	echo "[success] (slurm) compute_features test succeeded"
    jobid=${output//[^0-9]/}

	if [[ $slurm_available =~ "${slurm_true}" ]];
	then
		scancel $jobid
	fi
else
	echo "[failure] (slurm) compute_features test failed with output:"
	echo $output
	if [[ $slurm_available =~ "${slurm_true}" ]];
	then
		kill_started_jobs_slurm
	fi
fi

# TODO: Run the compute features locally
output_true="Computing features done!"
output=$(sparkle/CLI/compute_features.py --settings-file $sparkle_test_settings_path --run-on local | tail -1)

if [[ $output =~ "${output_true}" ]];
then
	echo "[success] (local) compute_features test succeeded"
else
	echo "[failure] (local) compute_features test failed with output:"
	echo $output
fi