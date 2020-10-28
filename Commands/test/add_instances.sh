#!/bin/bash

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/add_instances.sh
#SBATCH --output=TMP/add_instances.sh.txt
#SBATCH --error=TMP/add_instances.sh.err
#SBATCH --partition=graceADA
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1

# Initialise
Commands/initialise.py > /dev/null

# Add instances
instances_path="Examples/Resources/Instances/SAT_test"
output_true="c Adding instances SAT_test done!"
output_true_b="c Removing Sparkle report Components/Sparkle-latex-generator/Sparkle_Report.pdf done!"
output=$(Commands/add_instances.py --run-solver-later --run-extractor-later $instances_path | tail -1)

if [[ $output == $output_true ]] || [[ $output == $output_true_b ]];
then
	echo "[success] add_instances test succeeded"
else              
	echo "[failure] add_instances test failed with output:"
	echo $output
fi

