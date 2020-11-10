#!/bin/bash

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/save_record.sh
#SBATCH --output=TMP/save_record.sh.txt
#SBATCH --error=TMP/save_record.sh.err
#SBATCH --partition=graceADA
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1

# Initialise
Commands/initialise.py > /dev/null

# Save record
output_true_partA="c Record file Records/My_Record"
output_true_partB=".zip saved successfully!" # Somehow regex does not work when followed by this...
output=$(Commands/save_record.py | tail -1)

if [[ $output =~ ['${output_true_partA}'a-z0-9:._-] ]];
then
	echo "[success] save_record test succeeded"
else
	echo "[failure] save_record test failed with output:"
	echo $output
fi

