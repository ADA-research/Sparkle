#!/bin/bash

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/add_solver.sh
#SBATCH --output=Tmp/add_solver.sh.txt
#SBATCH --error=Tmp/add_solver.sh.err
#SBATCH --partition=graceADA
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1

# Initialise
sparkle/CLI/initialise.py > /dev/null

# Add solver
solver_path="Examples/Resources/Solvers/PbO-CCSAT-Generic"
output_true="Adding solver PbO-CCSAT-Generic done!"
output=$(sparkle/CLI/add_solver.py $solver_path | tail -1)

if [[ $output == $output_true ]];
then
	echo "[success] add_solver test succeeded"
else              
	echo "[failure] add_solver test failed with output:"
	echo $output
fi

