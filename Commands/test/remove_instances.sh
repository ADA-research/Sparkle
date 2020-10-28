#!/bin/bash

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/remove_instances.sh
#SBATCH --output=TMP/remove_instances.sh.txt
#SBATCH --error=TMP/remove_instances.sh.err
#SBATCH --partition=graceADA
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1

# Initialise
Commands/initialise.py > /dev/null

# Add instances
instances_name="PTN"
instances_source="Examples/Resources/Instances/$instances_name"
Commands/add_instances.py --run-solver-later --run-extractor-later $instances_source > /dev/null

# Remove instances
instances_path="Instances/$instances_name"
output_true="c Removing instances in directory $instances_path done!"
output=$(Commands/remove_instances.py $instances_path | tail -1)

if [[ $output == $output_true ]];
then
	echo "[success] remove_instances test succeeded"
else
	echo "[failure] remove_instances test failed with output:"
	echo $output
fi

