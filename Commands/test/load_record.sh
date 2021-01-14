#!/bin/bash

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/load_record.sh
#SBATCH --output=Tmp/load_record.sh.txt
#SBATCH --error=Tmp/load_record.sh.err
#SBATCH --partition=graceADA
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1

# Initialise
record_file="Commands/test/test_files/test_record.zip"
output_true="c Record file $record_file loaded successfully!"
output=$(Commands/load_record.py $record_file | tail -1)

if [[ $output == $output_true ]];
then
	echo "[success] load_record test succeeded"
else
	echo "[failure] load_record test failed with output:"
	echo $output
fi

