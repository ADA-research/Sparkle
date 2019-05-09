#!/bin/bash
###
#SBATCH --job-name=sparkle_run_default_wrapper.py_PTN_test_exp_sbatch.sh
#SBATCH --output=tmp/sparkle_run_default_wrapper.py_PTN_test_exp_sbatch.sh.txt
#SBATCH --error=tmp/sparkle_run_default_wrapper.py_PTN_test_exp_sbatch.sh.err
###
###
#SBATCH --partition=graceALL
#SBATCH --mem-per-cpu=3000
#SBATCH --array=0-11%12
###
params=( \
'results/sparkle_run_default_wrapper.py_PTN/sparkle_run_default_wrapper.py_Ptn-7824-b14.cnf_1.res ./sparkle_run_default_wrapper.py ./ ../instances_test/PTN/Ptn-7824-b14.cnf' \
'results/sparkle_run_default_wrapper.py_PTN/sparkle_run_default_wrapper.py_Ptn-7824-b02.cnf_1.res ./sparkle_run_default_wrapper.py ./ ../instances_test/PTN/Ptn-7824-b02.cnf' \
'results/sparkle_run_default_wrapper.py_PTN/sparkle_run_default_wrapper.py_Ptn-7824-b05.cnf_1.res ./sparkle_run_default_wrapper.py ./ ../instances_test/PTN/Ptn-7824-b05.cnf' \
'results/sparkle_run_default_wrapper.py_PTN/sparkle_run_default_wrapper.py_Ptn-7824-b15.cnf_1.res ./sparkle_run_default_wrapper.py ./ ../instances_test/PTN/Ptn-7824-b15.cnf' \
'results/sparkle_run_default_wrapper.py_PTN/sparkle_run_default_wrapper.py_plain7824.cnf_1.res ./sparkle_run_default_wrapper.py ./ ../instances_test/PTN/plain7824.cnf' \
'results/sparkle_run_default_wrapper.py_PTN/sparkle_run_default_wrapper.py_Ptn-7824-b07.cnf_1.res ./sparkle_run_default_wrapper.py ./ ../instances_test/PTN/Ptn-7824-b07.cnf' \
'results/sparkle_run_default_wrapper.py_PTN/sparkle_run_default_wrapper.py_Ptn-7824-b18.cnf_1.res ./sparkle_run_default_wrapper.py ./ ../instances_test/PTN/Ptn-7824-b18.cnf' \
'results/sparkle_run_default_wrapper.py_PTN/sparkle_run_default_wrapper.py_Ptn-7824-b06.cnf_1.res ./sparkle_run_default_wrapper.py ./ ../instances_test/PTN/Ptn-7824-b06.cnf' \
'results/sparkle_run_default_wrapper.py_PTN/sparkle_run_default_wrapper.py_Ptn-7824-b01.cnf_1.res ./sparkle_run_default_wrapper.py ./ ../instances_test/PTN/Ptn-7824-b01.cnf' \
'results/sparkle_run_default_wrapper.py_PTN/sparkle_run_default_wrapper.py_Ptn-7824-b08.cnf_1.res ./sparkle_run_default_wrapper.py ./ ../instances_test/PTN/Ptn-7824-b08.cnf' \
'results/sparkle_run_default_wrapper.py_PTN/sparkle_run_default_wrapper.py_Ptn-7824-b19.cnf_1.res ./sparkle_run_default_wrapper.py ./ ../instances_test/PTN/Ptn-7824-b19.cnf' \
'results/sparkle_run_default_wrapper.py_PTN/sparkle_run_default_wrapper.py_Ptn-7824-b17.cnf_1.res ./sparkle_run_default_wrapper.py ./ ../instances_test/PTN/Ptn-7824-b17.cnf' \
)
srun -N1 -n1 --exclusive  ./runsolver --timestamp --use-pty -C 60 -o  ${params[$SLURM_ARRAY_TASK_ID]}
