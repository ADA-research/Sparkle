#!/bin/bash

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/about.sh
#SBATCH --output=TMP/about.sh.txt
#SBATCH --error=TMP/about.sh.err
#SBATCH --partition=graceADA
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1

# Activate environment
source activate sparkle_test &> /dev/null

# Initialise
Commands/initialise.py > /dev/null

# Save record
output_true="c For more details see README.md"
output=$(Commands/about.py | tail -1)

if [[ $output == $output_true ]];
then
	echo "[success] about test succeeded"
else
	echo "[failure] about test failed with output:"
	echo $output
fi

