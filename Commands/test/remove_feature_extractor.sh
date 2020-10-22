#!/bin/bash

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/remove_record.sh
#SBATCH --output=TMP/remove_record.sh.txt
#SBATCH --error=TMP/remove_record.sh.err
#SBATCH --partition=graceADA
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1

# Activate environment
source activate sparkle_test &> /dev/null

# Initialise
Commands/initialise.py > /dev/null

# Add feature extractor
extractor_name="SAT-features-competition2012_revised_without_SatELite_sparkle"
extractor_source="Examples/Resources/Extractors/$extractor_name"
Commands/add_feature_extractor.py --run-extractor-later $extractor_source > /dev/null

# Remove feature extractor
extractor_path="Extractors/$extractor_name"
output_true="c Removing feature extractor $extractor_name done!"
output=$(Commands/remove_feature_extractor.py $extractor_path | tail -1)

if [[ $output == $output_true ]];
then
	echo "[success] remove_feature_extractor test succeeded"
else
	echo "[failure] remove_feature_extractor test failed with output:"
	echo $output
fi

