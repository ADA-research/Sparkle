#!/bin/bash
###
#SBATCH --job-name=PbO-CCSAT-Generic_PTN_scenario.txt_25_exp_sbatch.sh
#SBATCH --output=tmp/PbO-CCSAT-Generic_PTN_scenario.txt_25_exp_sbatch.sh.txt
#SBATCH --error=tmp/PbO-CCSAT-Generic_PTN_scenario.txt_25_exp_sbatch.sh.err
###
###
#SBATCH --partition=graceALL
#SBATCH --mem-per-cpu=3000
#SBATCH --array=0-24%25
###
params=( \
'example_scenarios/PbO-CCSAT-Generic/PbO-CCSAT-Generic_PTN_scenario.txt 1 results/PbO-CCSAT-Generic_PTN/PbO-CCSAT-Generic_PTN_scenario.txt_25_exp_sbatch.sh_seed_1_smac.txt' \
'example_scenarios/PbO-CCSAT-Generic/PbO-CCSAT-Generic_PTN_scenario.txt 2 results/PbO-CCSAT-Generic_PTN/PbO-CCSAT-Generic_PTN_scenario.txt_25_exp_sbatch.sh_seed_2_smac.txt' \
'example_scenarios/PbO-CCSAT-Generic/PbO-CCSAT-Generic_PTN_scenario.txt 3 results/PbO-CCSAT-Generic_PTN/PbO-CCSAT-Generic_PTN_scenario.txt_25_exp_sbatch.sh_seed_3_smac.txt' \
'example_scenarios/PbO-CCSAT-Generic/PbO-CCSAT-Generic_PTN_scenario.txt 4 results/PbO-CCSAT-Generic_PTN/PbO-CCSAT-Generic_PTN_scenario.txt_25_exp_sbatch.sh_seed_4_smac.txt' \
'example_scenarios/PbO-CCSAT-Generic/PbO-CCSAT-Generic_PTN_scenario.txt 5 results/PbO-CCSAT-Generic_PTN/PbO-CCSAT-Generic_PTN_scenario.txt_25_exp_sbatch.sh_seed_5_smac.txt' \
'example_scenarios/PbO-CCSAT-Generic/PbO-CCSAT-Generic_PTN_scenario.txt 6 results/PbO-CCSAT-Generic_PTN/PbO-CCSAT-Generic_PTN_scenario.txt_25_exp_sbatch.sh_seed_6_smac.txt' \
'example_scenarios/PbO-CCSAT-Generic/PbO-CCSAT-Generic_PTN_scenario.txt 7 results/PbO-CCSAT-Generic_PTN/PbO-CCSAT-Generic_PTN_scenario.txt_25_exp_sbatch.sh_seed_7_smac.txt' \
'example_scenarios/PbO-CCSAT-Generic/PbO-CCSAT-Generic_PTN_scenario.txt 8 results/PbO-CCSAT-Generic_PTN/PbO-CCSAT-Generic_PTN_scenario.txt_25_exp_sbatch.sh_seed_8_smac.txt' \
'example_scenarios/PbO-CCSAT-Generic/PbO-CCSAT-Generic_PTN_scenario.txt 9 results/PbO-CCSAT-Generic_PTN/PbO-CCSAT-Generic_PTN_scenario.txt_25_exp_sbatch.sh_seed_9_smac.txt' \
'example_scenarios/PbO-CCSAT-Generic/PbO-CCSAT-Generic_PTN_scenario.txt 10 results/PbO-CCSAT-Generic_PTN/PbO-CCSAT-Generic_PTN_scenario.txt_25_exp_sbatch.sh_seed_10_smac.txt' \
'example_scenarios/PbO-CCSAT-Generic/PbO-CCSAT-Generic_PTN_scenario.txt 11 results/PbO-CCSAT-Generic_PTN/PbO-CCSAT-Generic_PTN_scenario.txt_25_exp_sbatch.sh_seed_11_smac.txt' \
'example_scenarios/PbO-CCSAT-Generic/PbO-CCSAT-Generic_PTN_scenario.txt 12 results/PbO-CCSAT-Generic_PTN/PbO-CCSAT-Generic_PTN_scenario.txt_25_exp_sbatch.sh_seed_12_smac.txt' \
'example_scenarios/PbO-CCSAT-Generic/PbO-CCSAT-Generic_PTN_scenario.txt 13 results/PbO-CCSAT-Generic_PTN/PbO-CCSAT-Generic_PTN_scenario.txt_25_exp_sbatch.sh_seed_13_smac.txt' \
'example_scenarios/PbO-CCSAT-Generic/PbO-CCSAT-Generic_PTN_scenario.txt 14 results/PbO-CCSAT-Generic_PTN/PbO-CCSAT-Generic_PTN_scenario.txt_25_exp_sbatch.sh_seed_14_smac.txt' \
'example_scenarios/PbO-CCSAT-Generic/PbO-CCSAT-Generic_PTN_scenario.txt 15 results/PbO-CCSAT-Generic_PTN/PbO-CCSAT-Generic_PTN_scenario.txt_25_exp_sbatch.sh_seed_15_smac.txt' \
'example_scenarios/PbO-CCSAT-Generic/PbO-CCSAT-Generic_PTN_scenario.txt 16 results/PbO-CCSAT-Generic_PTN/PbO-CCSAT-Generic_PTN_scenario.txt_25_exp_sbatch.sh_seed_16_smac.txt' \
'example_scenarios/PbO-CCSAT-Generic/PbO-CCSAT-Generic_PTN_scenario.txt 17 results/PbO-CCSAT-Generic_PTN/PbO-CCSAT-Generic_PTN_scenario.txt_25_exp_sbatch.sh_seed_17_smac.txt' \
'example_scenarios/PbO-CCSAT-Generic/PbO-CCSAT-Generic_PTN_scenario.txt 18 results/PbO-CCSAT-Generic_PTN/PbO-CCSAT-Generic_PTN_scenario.txt_25_exp_sbatch.sh_seed_18_smac.txt' \
'example_scenarios/PbO-CCSAT-Generic/PbO-CCSAT-Generic_PTN_scenario.txt 19 results/PbO-CCSAT-Generic_PTN/PbO-CCSAT-Generic_PTN_scenario.txt_25_exp_sbatch.sh_seed_19_smac.txt' \
'example_scenarios/PbO-CCSAT-Generic/PbO-CCSAT-Generic_PTN_scenario.txt 20 results/PbO-CCSAT-Generic_PTN/PbO-CCSAT-Generic_PTN_scenario.txt_25_exp_sbatch.sh_seed_20_smac.txt' \
'example_scenarios/PbO-CCSAT-Generic/PbO-CCSAT-Generic_PTN_scenario.txt 21 results/PbO-CCSAT-Generic_PTN/PbO-CCSAT-Generic_PTN_scenario.txt_25_exp_sbatch.sh_seed_21_smac.txt' \
'example_scenarios/PbO-CCSAT-Generic/PbO-CCSAT-Generic_PTN_scenario.txt 22 results/PbO-CCSAT-Generic_PTN/PbO-CCSAT-Generic_PTN_scenario.txt_25_exp_sbatch.sh_seed_22_smac.txt' \
'example_scenarios/PbO-CCSAT-Generic/PbO-CCSAT-Generic_PTN_scenario.txt 23 results/PbO-CCSAT-Generic_PTN/PbO-CCSAT-Generic_PTN_scenario.txt_25_exp_sbatch.sh_seed_23_smac.txt' \
'example_scenarios/PbO-CCSAT-Generic/PbO-CCSAT-Generic_PTN_scenario.txt 24 results/PbO-CCSAT-Generic_PTN/PbO-CCSAT-Generic_PTN_scenario.txt_25_exp_sbatch.sh_seed_24_smac.txt' \
'example_scenarios/PbO-CCSAT-Generic/PbO-CCSAT-Generic_PTN_scenario.txt 25 results/PbO-CCSAT-Generic_PTN/PbO-CCSAT-Generic_PTN_scenario.txt_25_exp_sbatch.sh_seed_25_smac.txt' \
)
srun -N1 -n1 --exclusive  ./each_smac_run_core.sh  ${params[$SLURM_ARRAY_TASK_ID]}
