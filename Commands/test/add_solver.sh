#!/bin/bash

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/add_solver.sh
#SBATCH --output=TMP/add_solver.sh.txt
#SBATCH --error=TMP/add_solver.sh.err
#SBATCH --partition=graceADA
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1

# Initialise
Commands/initialise.py > /dev/null

# Add solver
solver_path="Examples/Resources/Solvers/PbO-CCSAT-Generic"
output_true="c Adding solver PbO-CCSAT-Generic done!"
output_true_b="c Removing Sparkle report Components/Sparkle-latex-generator/Sparkle_Report.pdf done!"
output=$(Commands/add_solver.py --run-solver-later --deterministic 0 $solver_path | tail -1)

if [[ $output == $output_true ]] || [[ $output == $output_true_b ]];
then
	echo "[success] add_solver test succeeded"
else              
	echo "[failure] add_solver test failed with output:"
	echo $output
fi

