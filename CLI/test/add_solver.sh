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
CLI/initialise.py > /dev/null

# Add solver
solver_path="Examples/Resources/Solvers/PbO-CCSAT-Generic"
output_true="Adding solver PbO-CCSAT-Generic done!"
output_true_b="Removing Sparkle report Components/Sparkle-latex-generator/Sparkle_Report.pdf done!"
output=$(CLI/add_solver.py --deterministic 0 $solver_path | tail -1)

if [[ $output == $output_true ]] || [[ $output == $output_true_b ]];
then
	echo "[success] add_solver test succeeded"
else              
	echo "[failure] add_solver test failed with output:"
	echo $output
fi

