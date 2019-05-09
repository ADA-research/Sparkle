#!/bin/bash
###
#SBATCH --job-name=sparkle_run_configured_wrapper.sh_PTN_train_exp_sbatch.sh
#SBATCH --output=tmp/sparkle_run_configured_wrapper.sh_PTN_train_exp_sbatch.sh.txt
#SBATCH --error=tmp/sparkle_run_configured_wrapper.sh_PTN_train_exp_sbatch.sh.err
###
###
#SBATCH --partition=graceALL
#SBATCH --mem-per-cpu=3000
#SBATCH --array=0-10%11
###
params=( \
'results_train/sparkle_run_configured_wrapper.sh_PTN/sparkle_run_configured_wrapper.sh_Ptn-7824-b04.cnf_1.res ./sparkle_run_configured_wrapper.sh ./ ../instances/PTN/Ptn-7824-b04.cnf' \
'results_train/sparkle_run_configured_wrapper.sh_PTN/sparkle_run_configured_wrapper.sh_Ptn-7824-b03.cnf_1.res ./sparkle_run_configured_wrapper.sh ./ ../instances/PTN/Ptn-7824-b03.cnf' \
'results_train/sparkle_run_configured_wrapper.sh_PTN/sparkle_run_configured_wrapper.sh_Ptn-7824-b12.cnf_1.res ./sparkle_run_configured_wrapper.sh ./ ../instances/PTN/Ptn-7824-b12.cnf' \
'results_train/sparkle_run_configured_wrapper.sh_PTN/sparkle_run_configured_wrapper.sh_Ptn-7824-b20.cnf_1.res ./sparkle_run_configured_wrapper.sh ./ ../instances/PTN/Ptn-7824-b20.cnf' \
'results_train/sparkle_run_configured_wrapper.sh_PTN/sparkle_run_configured_wrapper.sh_Ptn-7824-b21.cnf_1.res ./sparkle_run_configured_wrapper.sh ./ ../instances/PTN/Ptn-7824-b21.cnf' \
'results_train/sparkle_run_configured_wrapper.sh_PTN/sparkle_run_configured_wrapper.sh_Ptn-7824-b13.cnf_1.res ./sparkle_run_configured_wrapper.sh ./ ../instances/PTN/Ptn-7824-b13.cnf' \
'results_train/sparkle_run_configured_wrapper.sh_PTN/sparkle_run_configured_wrapper.sh_Ptn-7824-b10.cnf_1.res ./sparkle_run_configured_wrapper.sh ./ ../instances/PTN/Ptn-7824-b10.cnf' \
'results_train/sparkle_run_configured_wrapper.sh_PTN/sparkle_run_configured_wrapper.sh_Ptn-7824-b16.cnf_1.res ./sparkle_run_configured_wrapper.sh ./ ../instances/PTN/Ptn-7824-b16.cnf' \
'results_train/sparkle_run_configured_wrapper.sh_PTN/sparkle_run_configured_wrapper.sh_Ptn-7824-b11.cnf_1.res ./sparkle_run_configured_wrapper.sh ./ ../instances/PTN/Ptn-7824-b11.cnf' \
'results_train/sparkle_run_configured_wrapper.sh_PTN/sparkle_run_configured_wrapper.sh_bce7824.cnf_1.res ./sparkle_run_configured_wrapper.sh ./ ../instances/PTN/bce7824.cnf' \
'results_train/sparkle_run_configured_wrapper.sh_PTN/sparkle_run_configured_wrapper.sh_Ptn-7824-b09.cnf_1.res ./sparkle_run_configured_wrapper.sh ./ ../instances/PTN/Ptn-7824-b09.cnf' \
)
srun -N1 -n1 --exclusive  ./runsolver --timestamp --use-pty -C 60 -o  ${params[$SLURM_ARRAY_TASK_ID]}
