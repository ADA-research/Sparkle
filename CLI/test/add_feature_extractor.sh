#!/bin/bash

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/add_feature_extractor.sh
#SBATCH --output=Tmp/add_feature_extractor.sh.txt
#SBATCH --error=Tmp/add_feature_extractor.sh.err
#SBATCH --partition=graceADA
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1

# Initialise
CLI/initialise.py > /dev/null

# Add feature extractor
extractor_path="Examples/Resources/Extractors/SAT-features-competition2012_revised_without_SatELite_sparkle"
output_true="Adding feature extractor SAT-features-competition2012_revised_without_SatELite_sparkle done!"
output_true_b="Removing Sparkle report Components/Sparkle-latex-generator/Sparkle_Report.pdf done!"
output=$(CLI/add_feature_extractor.py $extractor_path | tail -1)

if [[ $output == $output_true ]] || [[ $output == $output_true_b ]];
then
	echo "[success] add_feature_extractor test succeeded"
else              
	echo "[failure] add_feature_extractor test failed with output:"
	echo $output
fi

