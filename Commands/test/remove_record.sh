#!/bin/bash

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/remove_record.sh
#SBATCH --output=TMP/remove_record.sh.txt
#SBATCH --error=TMP/remove_record.sh.err
#SBATCH --partition=graceADA
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1

# Activate environment
source activate sparkle_test &> /dev/null

# Remove record
record_file_origin="Commands/test/test_files/test_record.zip"
record_dir="Records/"
record_file="${record_dir}test_record.zip"
mkdir $record_dir &> /dev/null
cp $record_file_origin $record_file
output_true="c Record file $record_file removed!"
output=$(Commands/remove_record.py $record_file | tail -1)

if [[ $output == $output_true ]];
then
	echo "[success] remove_record test succeeded"
else
	echo "[failure] remove_record test failed with output:"
	echo $output
fi

