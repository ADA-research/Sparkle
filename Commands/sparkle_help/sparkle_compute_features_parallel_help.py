#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
'''Helper functions for parallel feature computation.'''

import sys

try:
    from sparkle_help import sparkle_feature_data_csv_help as sfdcsv
    from sparkle_help import sparkle_job_help
    from sparkle_help import sparkle_compute_features_help as scf
    from sparkle_help import sparkle_slurm_help as ssh
    from sparkle_help import sparkle_logging as sl
    from sparkle_help.sparkle_command_help import CommandName
except ImportError:
    import sparkle_feature_data_csv_help as sfdcsv
    import sparkle_job_help
    import sparkle_compute_features_help as scf
    import sparkle_slurm_help as ssh
    import sparkle_logging as sl
    from sparkle_command_help import CommandName


def computing_features_parallel(feature_data_csv_path, mode):
    '''
    Compute features in parallel.

    The 1st argument (feature_data_csv_path) specifies the path of the csv file where the
    resulting feature data would be placed.
    The 2nd argument (mode) specifies the mode of computation. It has 2 possible values
    (1 or 2). If this value is 1, it means that this function will compute the remaining
    jobs for feature computation. Otherwise (if this value is 2), it means that this
    function will re-compute all jobs for feature computation.
    '''
    # Open the csv file in terms of feature data
    feature_data_csv = sfdcsv.SparkleFeatureDataCSV(feature_data_csv_path)

    if mode == 1:
        # The value of mode is 1, so the list of computation jobs is the list of the
        # remaining jobs
        list_feature_computation_job = (
            feature_data_csv.get_list_remaining_feature_computation_job())
    elif mode == 2:
        # The value of mode is 2, so the list of computation jobs is the list of all jobs
        # (recomputing)
        list_feature_computation_job = (
            feature_data_csv.get_list_recompute_feature_computation_job())
    else:  # The abnormal case, exit
        print('Computing features mode error!')
        print('Do not compute features')
        sys.exit()

    ####
    # Expand the job list
    total_job_num = (
        sparkle_job_help.get_num_of_total_job_from_list(list_feature_computation_job))

    # If there are no jobs, stop
    if total_job_num < 1:
        print('No feature computation jobs to run; stopping execution! To recompute '
              'feature values use the --recompute flag.')
        sys.exit()
    # If there are jobs update feature data ID
    else:
        scf.update_feature_data_id()

    print('The number of total running jobs: ' + str(total_job_num))
    total_job_list = (
        sparkle_job_help.expand_total_job_from_list(list_feature_computation_job))
    ####

    ####
    # Generate the sbatch script
    n_jobs = len(total_job_list)
    sbatch_script_name, sbatch_script_dir = (
        ssh.generate_sbatch_script_for_feature_computation(n_jobs, feature_data_csv_path,
                                                           total_job_list))
    ####

    execution_dir = './'
    sbatch_script_path = sbatch_script_dir + sbatch_script_name
    # Execute the sbatch script via slurm
    jobid = ssh.submit_sbatch_script(sbatch_script_path, CommandName.COMPUTE_FEATURES,
                                     execution_dir)

    # Log output paths
    sl.add_output(sbatch_script_path,
                  'Slurm batch script to compute features in parallel')

    return jobid
