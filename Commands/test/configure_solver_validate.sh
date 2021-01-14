#!/bin/bash

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/configure_solver.sh
#SBATCH --output=Tmp/configure_solver.sh.txt
#SBATCH --error=Tmp/configure_solver.sh.err
#SBATCH --partition=graceADA
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1

# Activate environment
source activate sparkle_test &> /dev/null

# Prepare for test
instances_path="Examples/Resources/Instances/PTN/"
solver_path="Examples/Resources/Solvers/PbO-CCSAT-Generic/"

Commands/initialise.py > /dev/null
Commands/add_instances.py --run-solver-later --run-extractor-later $instances_path > /dev/null
Commands/add_solver.py --run-solver-later --deterministic 0 $solver_path > /dev/null

# Configure solver
output=$(Commands/configure_solver.py --validate --ablation --solver $solver_path --instance-set-train $instances_path | tail -1)

validationcallbackfile=Tmp/delayed_validation_PbO-CCSAT-Generic_PTN_script.sh
ablationcallbackfile=Tmp/delayed_ablation_PbO-CCSAT-Generic_PTN_script.sh


if [ ! -f "$validationcallbackfile" ]; then
    echo "[failure] $validationcallbackfile does not exist for configure_solver_validation."
elif [ ! -f "$ablationcallbackfile" ]; then
    echo "[failure] $ablationcallbackfile does not exist for configure_solver_validation."
else              
	echo "[failure] configure_solver_validation test failed with output:"
	echo $output
fi