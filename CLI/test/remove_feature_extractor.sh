#!/bin/bash

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/remove_feature_extractor.sh
#SBATCH --output=Tmp/remove_feature_extractor.sh.txt
#SBATCH --error=Tmp/remove_feature_extractor.sh.err
#SBATCH --partition=graceADA
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1

# Initialise
CLI/initialise.py > /dev/null

# Add feature extractor
extractor_name="SAT-features-competition2012_revised_without_SatELite_sparkle"
extractor_source="Examples/Resources/Extractors/$extractor_name"
CLI/add_feature_extractor.py $extractor_source > /dev/null

# Remove feature extractor
extractor_path="Extractors/$extractor_name"
output_true="Removing feature extractor $extractor_name done!"
output=$(CLI/remove_feature_extractor.py $extractor_path | tail -1)

if [[ $output == $output_true ]];
then
	echo "[success] remove_feature_extractor test succeeded"
else
	echo "[failure] remove_feature_extractor test failed with output:"
	echo $output
fi

