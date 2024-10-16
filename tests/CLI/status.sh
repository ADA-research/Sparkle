#!/bin/bash

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/status.sh
#SBATCH --output=Tmp/status.sh.txt
#SBATCH --error=Tmp/status.sh.err
#SBATCH --partition=graceADA
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1

# System status
output_true="Current system status of Sparkle reported!"
output=$(sparkle/CLI/status.py | tail -1)

if [[ $output == $output_true ]];
then
	echo "[success] system_status test succeeded"
else
	echo "[failure] system_status test failed with output:"
	echo $output
fi

