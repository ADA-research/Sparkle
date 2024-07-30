#!/bin/bash

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/load_snapshot.sh
#SBATCH --output=Tmp/load_snapshot.sh.txt
#SBATCH --error=Tmp/load_snapshot.sh.err
#SBATCH --partition=graceADA
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1

# Initialise
snapshot_file="tests/CLI/test_files/test_snapshot.zip"
output_true="Snapshot file $snapshot_file loaded successfully!"
output=$(sparkle/CLI/load_snapshot.py $snapshot_file | tail -1)

if [[ $output == $output_true ]];
then
	echo "[success] load_snapshot test succeeded"
else
	echo "[failure] load_snapshot test failed with output:"
	echo $output
fi
