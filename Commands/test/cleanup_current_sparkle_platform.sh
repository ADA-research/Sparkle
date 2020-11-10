#!/bin/bash

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/cleanup_current_sparkle_platform.sh
#SBATCH --output=TMP/cleanup_current_sparkle_platform.sh.txt
#SBATCH --error=TMP/cleanup_current_sparkle_platform.sh.err
#SBATCH --partition=graceADA
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1

# Initialise
Commands/initialise.py > /dev/null

# Cleanup current sparkle platform
output_true="c Existing Sparkle platform cleaned!"
output=$(Commands/cleanup_current_sparkle_platform.py | tail -1)

if [[ $output == $output_true ]];
then
	echo "[success] cleanup_current_sparkle_platform test succeeded"
else              
	echo "[failure] cleanup_current_sparkle_platform test failed with output:"
	echo $output
fi

