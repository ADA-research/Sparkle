# Output Paths

## Configuration

Path: ../../Components/smac-v2.10.03-master-778/
File: <solver_name>_<instance_set>_scenario.txt_<number_of_configuration_runs>_exp_sbatch.sh
Description: sbatch script that executes configuration experiments through Slurm
Output:
  Slurm stderr: tmp/<solver_name>_<instance_set>_scenario.txt_<number_of_configuration_runs>_exp_sbatch.sh.err
  Slurm stdout: tmp/<solver_name>_<instance_set>_scenario.txt_<number_of_configuration_runs>_exp_sbatch.sh.txt
  Configurator log: results/<solver_name>_<instance_set>/<solver_name>_<instance_set>_scenario.txt_<number_of_configuration_runs>_exp_sbatch.sh_seed_<run_id>_smac.txt
  Execution directory: example_scenarios/<solver_name>/<run_id>/
  Configurator detailed output: example_scenarios/cadical-sc17_for_sparkle/outdir_train_configuration/cadical-sc17_for_sparkle_train_scenario/
  Validation log: log-val-1.txt

Other:
  Scenario file: example_scenarios/<solver_name>/<solver_name>_train_scenario.txt
  Last solver and instance set used for configuration: example_scenarios/cadical-sc17_for_sparkle/last_configuration.txt
 Last solver, training-, and testing instance sets used for validation: example_scenarios/cadical-sc17_for_sparkle/last_test_configured_default.txt
  Training instances: <instance_set>_train.txt

## Validation

Path: ../../Components/smac-v2.10.03-master-778/
File: <solver_name>_<instance_set>_validation_sbatch.sh
Output:
  Slurm stderr: tmp/<solver_name>_<instance_set>_validation_sbatch.sh.err
  Slurm stdout: tmp/<solver_name>_<instance_set>_validation_sbatch.sh.txt
  Validation log: results/<solver_name>_validation_train_train_default_scenario.txt
Description: sbatch script that executes validation experiments through Slurm
