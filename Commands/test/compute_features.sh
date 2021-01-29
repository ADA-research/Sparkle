#!/bin/bash

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/compute_features.sh
#SBATCH --output=Tmp/compute_features.sh.txt
#SBATCH --error=Tmp/compute_features.sh.err
#SBATCH --partition=graceADA
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1

# Settings
sparkle_test_settings_path="Commands/test/test_files/sparkle_settings.ini"

# Prepare for test
instances_path="Examples/Resources/Instances/PTN"
extractor_path="Examples/Resources/Extractors/SAT-features-competition2012_revised_without_SatELite_sparkle"

Commands/initialise.py > /dev/null
Commands/add_instances.py --run-solver-later --run-extractor-later $instances_path > /dev/null
Commands/add_feature_extractor.py --run-extractor-later $extractor_path > /dev/null

# Compute features
output_true="c Computing features done!"
output=$(Commands/compute_features.py --settings-file $sparkle_test_settings_path | tail -1)

if [[ $output == $output_true ]];
then
	echo "[success] compute_features test succeeded"
else              
	echo "[failure] compute_features test failed with output:"
	echo $output
fi

# Compute features parallel
output_true="c Computing features in parallel ..."
output=$(Commands/compute_features.py --settings-file $sparkle_test_settings_path --parallel --recompute | tail -1)

if [[ $output == $output_true ]];
then
	echo "[success] compute_features --parallel test succeeded"
else              
	echo "[failure] compute_features --parallel test failed with output:"
	echo $output
fi

