#!/bin/bash

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/cleanup_temporary_files.sh
#SBATCH --output=Tmp/cleanup_temporary_files.sh.txt
#SBATCH --error=Tmp/cleanup_temporary_files.sh.err
#SBATCH --partition=graceADA
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1


# Cleanup temporary files
output_true="Cleaned platform of temporary files!"
output=$(sparkle/CLI/cleanup.py | tail -1)

if [[ $output == $output_true ]];
then
	echo "[success] cleanup test succeeded"
else
	echo "[failure] cleanup test failed with output:"
	echo $output
fi

