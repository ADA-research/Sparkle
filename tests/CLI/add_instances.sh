#!/bin/bash

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/add_instances.sh
#SBATCH --output=Tmp/add_instances.sh.txt
#SBATCH --error=Tmp/add_instances.sh.err
#SBATCH --partition=graceADA
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1

# Initialise
sparkle/CLI/initialise.py > /dev/null

# Add instances
instances_path="Examples/Resources/Instances/PTN"
output_true="Adding instance set PTN done!"
output_true_b=""
output=$(sparkle/CLI/add_instances.py $instances_path | tail -1)

if [[ $output == $output_true ]] || [[ $output == $output_true_b ]];
then
	echo "[success] add_instances test succeeded"
else              
	echo "[failure] add_instances test failed with output:"
	echo $output
fi

# Add multi-file instances
instances_path="Examples/Resources/CCAG/Instances/CCAG/"
output_true="Adding instance set CCAG done!"
output=$(sparkle/CLI/add_instances.py $instances_path | tail -1)

if [[ $output == $output_true ]] || [[ $output == $output_true_b ]];
then
	echo "[success] add_instances for multi-file instances test succeeded"
else              
	echo "[failure] add_instances for multi-file instances test failed with output:"
	echo $output
fi

