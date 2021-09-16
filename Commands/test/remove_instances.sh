#!/bin/bash

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/remove_instances.sh
#SBATCH --output=Tmp/remove_instances.sh.txt
#SBATCH --error=Tmp/remove_instances.sh.err
#SBATCH --partition=graceADA
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1

# Initialise
Commands/initialise.py > /dev/null

# Add instances
instances_name="PTN"
instances_source="Examples/Resources/Instances/$instances_name"
Commands/add_instances.py $instances_source > /dev/null

# Remove instances
instances_path="Instances/$instances_name"
output_true="c Removing instances in directory $instances_path done!"
output=$(Commands/remove_instances.py $instances_path | tail -1)

if [[ $output == $output_true ]];
then
	echo "[success] remove_instances test succeeded"
else
	echo "[failure] remove_instances test failed with output:"
	echo $output
fi

# Remove multi-file instances

instances_name="CCAG/Instances/CCAG/"
instances_source="Examples/Resources/$instances_name"
Commands/add_instances.py $instances_source > /dev/null

instances_path="Instances/CCAG"
output_true="c Removing instances in directory $instances_path done!"
output=$(Commands/remove_instances.py $instances_path | tail -1)

if [[ $output == $output_true ]];
then
	echo "[success] remove_instances for multi-file instances test succeeded"
else
	echo "[failure] remove_instances for multi-file instances test failed with output:"
	echo $output
fi

