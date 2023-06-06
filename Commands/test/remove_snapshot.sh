#!/bin/bash

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/remove_snapshot.sh
#SBATCH --output=Tmp/remove_snapshot.sh.txt
#SBATCH --error=Tmp/remove_snapshot.sh.err
#SBATCH --partition=graceADA
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1

# Remove snapshot
snapshot_file_origin="Commands/test/test_files/test_snapshot.zip"
snapshot_dir="Snapshots/"
snapshot_file="${snapshot_dir}test_snapshot.zip"
mkdir $snapshot_dir &> /dev/null
cp $snapshot_file_origin $snapshot_file
output_true="Snapshot file $snapshot_file removed!"
output=$(Commands/remove_snapshot.py $snapshot_file | tail -1)

if [[ $output == $output_true ]];
then
	echo "[success] remove_snapshot test succeeded"
else
	echo "[failure] remove_snapshot test failed with output:"
	echo $output
fi

