#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for the execution of a portfolio selector."""

import os
import pathlib
import sys
import fcntl
from pathlib import Path

try:
    from sparkle_help import sparkle_basic_help
    from sparkle_help import sparkle_file_help as sfh
    from sparkle_help import sparkle_global_help as sgh
    from sparkle_help import sparkle_feature_data_csv_help as sfdcsv
    from sparkle_help import sparkle_performance_data_csv_help as spdcsv
    from sparkle_help import sparkle_run_solvers_help as srs
    from sparkle_help import sparkle_logging as sl
    from sparkle_help.reporting_scenario import ReportingScenario
    from sparkle_help.reporting_scenario import Scenario
    from sparkle_help import sparkle_instances_help as sih
    from sparkle_help.sparkle_command_help import CommandName
    from sparkle_help import sparkle_job_help as sjh
except ImportError:
    import sparkle_basic_help
    import sparkle_file_help as sfh
    import sparkle_global_help as sgh
    import sparkle_feature_data_csv_help as sfdcsv
    import sparkle_performance_data_csv_help as spdcsv
    import sparkle_run_solvers_help as srs
    import sparkle_logging as sl
    from reporting_scenario import ReportingScenario
    from reporting_scenario import Scenario
    import sparkle_instances_help as sih
    from sparkle_command_help import CommandName
    import sparkle_job_help as sjh


def get_list_feature_vector(extractor_path, instance_path, result_path,
                            cutoff_time_each_extractor_run):
    """Return the feature vector for an instance as a list."""
    runsolver_path = sgh.runsolver_path

    cutoff_time_each_run_option = f"--cpu-limit {str(cutoff_time_each_extractor_run)}"
    err_path = result_path.replace(".rawres", ".err")
    runsolver_watch_data_path = result_path.replace(".rawres", ".log")
    runsolver_watch_data_path_option = f"-w {runsolver_watch_data_path}"
    runsolver_value_data_path = result_path.replace(".rawres", ".val")
    runsolver_value_data_path_option = f"-v {runsolver_value_data_path}"

    command_line = (f"{runsolver_path} {cutoff_time_each_run_option} "
                    f"{runsolver_watch_data_path_option} "
                    f"{runsolver_value_data_path_option} {extractor_path}/"
                    f"{sgh.sparkle_run_default_wrapper} {extractor_path}/ "
                    f"{instance_path} {result_path} 2> {err_path}")

    try:
        os.system(command_line)
        with open(runsolver_value_data_path) as file:
            if "TIMEOUT=true" in file.read():
                print(f"****** WARNING: Feature vector computing on instance "
                      f"{instance_path} timed out! ******")
    except Exception:
        if not os.path.exists(result_path):
            sfh.create_new_empty_file(result_path)

    try:
        sfdcsv.SparkleFeatureDataCSV(result_path)
    except Exception:
        print(f"****** WARNING: Feature vector computing on instance {instance_path}"
              " failed! ******")
        print("****** WARNING: The feature vector of this instance will be imputed as "
              "the mean value of all other non-missing values! ******")
        feature_data_csv = sfdcsv.SparkleFeatureDataCSV(sgh.feature_data_csv_path)
        list_feature_vector = feature_data_csv.generate_mean_value_feature_vector()
    else:
        fin = open(result_path, "r+")
        fcntl.flock(fin.fileno(), fcntl.LOCK_EX)
        myline = fin.readline().strip()
        myline = fin.readline().strip()
        list_feature_vector = myline.split(",")
        del list_feature_vector[0]
        fin.close()

    command_line = f"rm -f {result_path}"
    os.system(command_line)
    command_line = f"rm -f {err_path}"
    os.system(command_line)
    command_line = f"rm -f {runsolver_watch_data_path}"
    os.system(command_line)
    command_line = f"rm -f {runsolver_value_data_path}"
    os.system(command_line)

    return list_feature_vector


def print_predict_schedule(predict_schedule_result_path: str) -> None:
    """Print the predicted algorithm schedule."""
    fin = open(predict_schedule_result_path, "r+")
    fcntl.flock(fin.fileno(), fcntl.LOCK_EX)
    myline = fin.readline().strip()
    print(myline)
    fin.close()

    return


def get_list_predict_schedule_from_file(predict_schedule_result_path: str):
    """Return the predicted algorithm schedule as a list."""
    list_predict_schedule = []
    prefix_string = "Selected Schedule [(algorithm, budget)]: "
    fin = open(predict_schedule_result_path, "r+")
    fcntl.flock(fin.fileno(), fcntl.LOCK_EX)
    predict_schedule = fin.readline().strip()

    if predict_schedule == "":
        print("ERROR: Failed to get schedule from algorithm portfolio. Stopping "
              "execution!\n"
              f"Schedule file appears to be empty: {predict_schedule_result_path}\n"
              f"Selector error output path: {sgh.sparkle_err_path}")
        sys.exit(-1)

    predict_schedule_string = predict_schedule[len(prefix_string):]
    list_predict_schedule = eval(predict_schedule_string)
    fin.close()

    return list_predict_schedule


def print_solution(raw_result_path) -> None:
    """Print the solution from a raw result."""
    fin = open(raw_result_path, "r+")
    fcntl.flock(fin.fileno(), fcntl.LOCK_EX)

    while True:
        myline = fin.readline().strip()

        if not myline:
            break
        mylist = myline.split()

        if mylist[1] == r"s" or mylist[1] == r"v":
            string_output = " ".join(mylist[1:])
            print(string_output)

    fin.close()

    return


def call_solver_solve_instance_within_cutoff(solver_path: str, instance_path: str,
                                             cutoff_time: int,
                                             performance_data_csv_path: str = None):
    """Call the Sparkle portfolio selector to solve a single instance with a cutoff."""
    _, _, cpu_time_penalised, _, status, raw_result_path = (
        srs.run_solver_on_instance_and_process_results(solver_path, instance_path,
                                                       custom_cutoff=cutoff_time))
    flag_solved = False

    if status == "SUCCESS" or status == "SAT" or status == "UNSAT":
        flag_solved = True

    if performance_data_csv_path is not None:
        solver_name = "Sparkle_Portfolio_Selector"
        check_selector_status(solver_name)
        fo = open(performance_data_csv_path, "r+")
        fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
        performance_data_csv = spdcsv.SparklePerformanceDataCSV(
            performance_data_csv_path)
        performance_data_csv.set_value(instance_path, solver_name, cpu_time_penalised)
        performance_data_csv.dataframe.to_csv(performance_data_csv_path)
        fo.close()
    else:
        if flag_solved:
            print("instance solved by solver " + solver_path)
            os.system("cat %s" % (raw_result_path))
        else:
            print(f"solver {solver_path} failed to solve the instance with status "
                  f"{status}")

    os.system(r"rm -f " + raw_result_path)

    return flag_solved


def call_sparkle_portfolio_selector_solve_instance(
        instance_path: str, performance_data_csv_path: str = None):
    """Call the Sparkle portfolio selector to solve a single instance."""
    # Create instance strings to accommodate multi-file instances
    instance_path_list = instance_path.split()
    instance_file_list = []

    for instance in instance_path_list:
        instance_file_list.append(sfh.get_last_level_directory_name(instance))

    instance_files_str = " ".join(instance_file_list)
    instance_files_str_ = "_".join(instance_file_list)

    print("Start running Sparkle portfolio selector on solving instance "
          f"{instance_files_str} ...")
    python_executable = sgh.python_executable
    if not os.path.exists("Tmp/"):
        os.mkdir("Tmp/")

    print("Sparkle computing features of instance " + instance_files_str + " ...")
    list_feature_vector = []

    if len(sgh.extractor_list) == 0:
        print("ERROR: No feature extractor added to Sparkle.")
        sys.exit()

    cutoff_time_each_extractor_run = (
        sgh.settings.get_general_extractor_cutoff_time() / len(sgh.extractor_list))

    for extractor_path in sgh.extractor_list:
        print(f"Extractor {sfh.get_last_level_directory_name(extractor_path)} computing "
              f"features of instance {instance_files_str} ...")
        result_path = (f"Tmp/{sfh.get_last_level_directory_name(extractor_path)}_"
                       f"{instance_files_str_}_"
                       f"{sparkle_basic_help.get_time_pid_random_string()}.rawres")

        list_feature_vector = list_feature_vector + get_list_feature_vector(
            extractor_path, instance_path, result_path, cutoff_time_each_extractor_run)
        print(f"Extractor {sfh.get_last_level_directory_name(extractor_path)} computing "
              f"features of instance {instance_files_str} done!")
    print("Sparkle computing features of instance " + instance_files_str + " done!")

    command_line = (f"{python_executable} {sgh.autofolio_path} --load "
                    f'{sgh.sparkle_portfolio_selector_path} --feature_vec "')
    for i in range(0, len(list_feature_vector)):
        command_line = command_line + str(list_feature_vector[i])

        if i < (len(list_feature_vector) - 1):
            command_line = command_line + " "

    predict_schedule_result_path = ("Tmp/predict_schedule_"
                                    f"{sparkle_basic_help.get_time_pid_random_string()}"
                                    ".predres")
    command_line += f'" 1> {predict_schedule_result_path} 2> {sgh.sparkle_err_path}'
    print("Sparkle portfolio selector predicting ...")
    os.system(command_line)
    print("Predicting done!")

    print_predict_schedule(predict_schedule_result_path)
    list_predict_schedule = get_list_predict_schedule_from_file(
        predict_schedule_result_path)

    os.system("rm -f " + predict_schedule_result_path)
    os.system("rm -f " + sgh.sparkle_err_path)

    for i in range(0, len(list_predict_schedule)):
        solver_path = list_predict_schedule[i][0]
        if i + 1 < len(list_predict_schedule):
            cutoff_time = list_predict_schedule[i][1]
        else:
            cutoff_time = list_predict_schedule[i][1]
        print(f"Calling solver {sfh.get_last_level_directory_name(solver_path)} with "
              f"time budget {str(cutoff_time)} for solving ...")
        sys.stdout.flush()
        flag_solved = call_solver_solve_instance_within_cutoff(
            solver_path, instance_path, cutoff_time, performance_data_csv_path)
        print(f"Calling solver {sfh.get_last_level_directory_name(solver_path)} done!")

        if flag_solved:
            break
        else:
            print("The instance is not solved in this call")

    return


def generate_running_sparkle_portfolio_selector_sbatch_shell_script(
        sbatch_shell_script_path, test_case_directory_path, performance_data_csv_path,
        list_jobs, start_index, end_index):
    """Generate a Slurm batch script to run the Sparkle portfolio selector."""
    num_job_in_parallel = sgh.settings.get_slurm_number_of_runs_in_parallel()
    # specify the name of this sbatch script
    job_name = sfh.get_file_name(sbatch_shell_script_path)
    # calculate the total number of jobs to be handled in this sbatch script
    num_job_total = end_index - start_index
    if num_job_in_parallel > num_job_total:
        # update the number of jobs in parallel accordingly if it is greater than the
        # total number of jobs
        num_job_in_parallel = num_job_total
    # specify the prefix of the executing command
    command_prefix = ("srun -N1 -n1 --exclusive python "
                      "Commands/sparkle_help/run_sparkle_portfolio_core.py ")

    fout = open(sbatch_shell_script_path, "w+")  # open the file of sbatch script
    # using the UNIX file lock to prevent other attempts to visit this sbatch script
    fcntl.flock(fout.fileno(), fcntl.LOCK_EX)

    # TODO: Use generic slurm batch generator
    ####
    # specify the options of sbatch in the top of this sbatch script
    fout.write("#!/bin/bash\n")  # use bash to execute this script
    fout.write("###\n")
    fout.write("###\n")
    # specify the job name in this sbatch script
    fout.write("#SBATCH --job-name=" + job_name + "\n")
    std_out_path = test_case_directory_path + "Tmp/" + job_name + ".txt"
    # specify the file for normal output
    fout.write("#SBATCH --output=" + std_out_path + "\n")
    std_err_path = test_case_directory_path + "Tmp/" + job_name + ".err"
    # specify the file for error output
    fout.write("#SBATCH --error=" + std_err_path + "\n")
    fout.write("###" + "\n")
    # using slurm job array and specify the number of jobs executing in parallel in this
    # sbatch script
    fout.write(f"#SBATCH --array=0-{str(num_job_total-1)}%{str(num_job_in_parallel)}\n")
    fout.write("###" + "\n")
    ####

    ####
    # specify the array of parameters for each command
    fout.write("params=( \\" + "\n")

    for i in range(start_index, end_index):
        instance_path = list_jobs[i][0]
        fout.write(f"' --instance {instance_path}' \\\n")

    fout.write(r")" + "\n")
    ####

    # specify the complete command
    command_line = (f"{command_prefix} " + "${params[$SLURM_ARRAY_TASK_ID]}"
                    f" --performance-data-csv {performance_data_csv_path}")

    fout.write(command_line + "\n")  # write the complete command in this sbatch script

    fout.close()  # close the file of the sbatch script

    # Log the sbatch file and (error) output locations
    sl.add_output(sbatch_shell_script_path,
                  "Slurm batch script to run the portfolio selector")
    sl.add_output(std_out_path,
                  "Slurm batch script to run the portfolio selector output")
    sl.add_output(std_err_path,
                  "Slurm batch script to run the portfolio selector error output")

    return


def call_sparkle_portfolio_selector_solve_instance_directory(
        instance_directory_path: str):
    """Call the Sparkle portfolio selector to solve all instances in a directory."""
    if instance_directory_path[-1] != "/":
        instance_directory_path += "/"

    instance_directory_path_last_level = sfh.get_last_level_directory_name(
        instance_directory_path)

    if instance_directory_path_last_level[-1] != "/":
        instance_directory_path_last_level += "/"

    test_case_directory_path = "Test_Cases/" + instance_directory_path_last_level

    # Initialise latest scenario
    global latest_scenario
    sgh.latest_scenario = ReportingScenario()

    # Update latest scenario
    sgh.latest_scenario.set_selection_test_case_directory(Path(test_case_directory_path))
    sgh.latest_scenario.set_latest_scenario(Scenario.SELECTION)
    # Write used scenario to file
    sgh.latest_scenario.write_scenario_ini()

    if not os.path.exists("Test_Cases/"):
        os.system("mkdir Test_Cases/")
    os.system("mkdir -p " + test_case_directory_path)
    os.system("mkdir -p " + test_case_directory_path + "Tmp/")

    test_performance_data_csv_name = "sparkle_performance_data.csv"
    test_performance_data_csv_path = (
        test_case_directory_path + test_performance_data_csv_name)
    spdcsv.SparklePerformanceDataCSV.create_empty_csv(test_performance_data_csv_path)
    test_performance_data_csv = spdcsv.SparklePerformanceDataCSV(
        test_performance_data_csv_path)

    total_job_list = []

    list_all_filename = sih.get_instance_list_from_path(Path(instance_directory_path))

    for filename in list_all_filename:
        paths = []

        for name in filename.split():
            path = instance_directory_path + name
            paths.append(path)

        filepath = " ".join(paths)
        test_performance_data_csv.add_row(filepath)
        total_job_list.append([filepath])

    solver_name = "Sparkle_Portfolio_Selector"
    check_selector_status(solver_name)
    test_performance_data_csv.add_column(solver_name)

    test_performance_data_csv.update_csv()

    i = 0
    j = len(total_job_list)
    sbatch_shell_script_path = (
        f"{test_case_directory_path}Tmp/running_sparkle_portfolio_selector_sbatch_shell_"
        f"script_{str(i)}_{str(j)}_{sparkle_basic_help.get_time_pid_random_string()}.sh")
    generate_running_sparkle_portfolio_selector_sbatch_shell_script(
        sbatch_shell_script_path, test_case_directory_path,
        test_performance_data_csv_path, total_job_list, i, j)
    os.system("chmod a+x " + sbatch_shell_script_path)
    command_line = "sbatch " + sbatch_shell_script_path

    output_list = os.popen(command_line).readlines()

    if len(output_list) > 0 and len(output_list[0].strip().split()) > 0:
        jobid = output_list[0].strip().split()[-1]
        # Add job to active job CSV
        sjh.write_active_job(jobid, CommandName.RUN_SPARKLE_PORTFOLIO_SELECTOR)
    else:
        jobid = ""

    return


def check_selector_status(solver_name):
    """Check if there is an selector at the given path.

    If it does not exist the function will terminate the whole program.
    """
    selector = pathlib.Path(f"{solver_name}/sparkle_portfolio_selector__@@SPARKLE@@__")
    if not selector.exists() or not selector.is_file():
        print("ERROR: The portfolio selector could not be found. Please make sure to "
              "first construct a portfolio selector.")
        sys.exit()
