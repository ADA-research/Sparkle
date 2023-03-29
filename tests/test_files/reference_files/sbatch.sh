#!/bin/bash
###
#SBATCH --job-name=Test-Solver_Test-Instance-Set_scenario.txt_2_exp_sbatch.sh
#SBATCH --output=tmp/Test-Solver_Test-Instance-Set_scenario.txt_2_exp_sbatch.sh.txt
#SBATCH --error=tmp/Test-Solver_Test-Instance-Set_scenario.txt_2_exp_sbatch.sh.err
###
###
#SBATCH --mem-per-cpu=3000
#SBATCH --array=0-2%2
###
params=( \
'scenarios/Test-Solver_Test-Instance-Set/Test-Solver_Test-Instance-Set_scenario.txt 1 results/Test-Solver_Test-Instance-Set/Test-Solver_Test-Instance-Set_scenario.txt_2_exp_sbatch.sh_seed_1_smac.txt scenarios/Test-Solver_Test-Instance-Set/1' \
'scenarios/Test-Solver_Test-Instance-Set/Test-Solver_Test-Instance-Set_scenario.txt 2 results/Test-Solver_Test-Instance-Set/Test-Solver_Test-Instance-Set_scenario.txt_2_exp_sbatch.sh_seed_2_smac.txt scenarios/Test-Solver_Test-Instance-Set/2' \
)
srun -N1 -n1  ./each_smac_run_core.sh ${params[$SLURM_ARRAY_TASK_ID]}
