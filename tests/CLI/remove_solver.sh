#!/bin/bash

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/remove_solver.sh
#SBATCH --output=Tmp/remove_solver.sh.txt
#SBATCH --error=Tmp/remove_solver.sh.err
#SBATCH --partition=graceADA
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1

# Initialise
sparkle/CLI/initialise.py > /dev/null

# Add solver
solver_name="PbO-CCSAT-Generic"
solver_source="Examples/Resources/Solvers/$solver_name"
sparkle/CLI/add_solver.py $solver_source > /dev/null

# Remove solver
solver_path="Solvers/$solver_name"
output_true="Removing solver $solver_name done!"
output=$(sparkle/CLI/remove_solver.py $solver_path | tail -1)

if [[ $output == $output_true ]];
then
	echo "[success] remove_solver test succeeded"
else
	echo "[failure] remove_solver test failed with output:"
	echo $output
fi

