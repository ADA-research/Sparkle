#!/bin/bash

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/add_feature_extractor.sh
#SBATCH --output=TMP/add_feature_extractor.sh.txt
#SBATCH --error=TMP/add_feature_extractor.sh.err
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
extractor_path="Examples/Resources/Extractors/SAT-features-competition2012_revised_without_SatELite_sparkle"
output_true="c Adding feature extractor SAT-features-competition2012_revised_without_SatELite_sparkle done!"
output=$(Commands/add_feature_extractor.py --run-extractor-later $extractor_path | tail -1)

if [[ $output == $output_true ]];
then
	echo "add_feature_extractor test succeeded"
else
	echo "add_feature_extractor test failed with output:"
	echo $output
fi

