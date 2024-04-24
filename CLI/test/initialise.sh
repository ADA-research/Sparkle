#!/bin/bash

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/initialise.sh
#SBATCH --output=Tmp/initialise.sh.txt
#SBATCH --error=Tmp/initialise.sh.err
#SBATCH --partition=graceADA
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1

# Initialise
output_true="New Sparkle platform initialised!"
output=$(CLI/initialise.py | tail -1)

if [[ $output == $output_true ]];
then
	echo "[success] initialise test succeeded"
else
	echo "[failure] initialise test failed with output:"
	echo $output
fi

