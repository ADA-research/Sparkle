#!/bin/bash

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/about.sh
#SBATCH --output=Tmp/about.sh.txt
#SBATCH --error=Tmp/about.sh.err
#SBATCH --partition=graceADA
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1


# Save record
output_true="For more details see README.md"
output=$(sparkle/CLI/about.py | tail -1)

if [[ $output == $output_true ]];
then
	echo "[success] about test succeeded"
else
	echo "[failure] about test failed with output:"
	echo $output
fi

