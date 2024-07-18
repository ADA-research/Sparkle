Ablation Analysis standalone package
2020 October 22

The ablation analysis package is provided under the terms of the GNU Affero
General Public License v3.0. See the provided LICENSE.txt for more details.


This directory contains a beta release of the standalone implementation of
ablation analysis, a procedure used to analyse the difference between two
algorithm parameter configurations.

In order to run the ablation analysis itself, simply use the "ablationAnalysis"
script included in the release:

"./ablationAnalysis <options>"

OR

"./ablationAnalysis --optionFile <file containing command-line options>"


This will run the ablation analysis procedure using the instances specified in
the "instance_file" command-line or optionFile argument.

A sample option file has been included in "example_spear_small/ablation_spear_small.txt",
which will run ablation analysis using the SAT solver SPEAR on a small
subset of easy QCP instances.

"./ablationAnalysis --optionFile example_spear_small/ablation_spear_small.txt"



After the ablation analysis has completed, you can perform validation on
the resulting trajectory (using the "test_instance_file" instances from the
command-line or optionFile settings):

"./ablationValidation <options>"

OR

./ablationValidation --optionFile <file containing command-line options>"


You can find the trajectory from your initial ablation analysis run in the
log/ subdirectory, with the format "ablation-run<seed>.txt". You will want
to rename/move this file before running validation.

You specify the location of the ablation trajectory file with the 
"--ablationLogFile" command-line argument. If you wish to use more than 1
run per instance in the validation set, you can modify this with the
"--targetRunsPerInstance" argument.

Continuing the running example:

"mv log/ablation-run1234.txt ./trajectory"
"./ablationValidation --optionFile example_spear_small/ablation_spear_small.txt --ablationLogFile ./trajectory --targetRunsPerInstance 5"

A table with the results will be printed to console when validation is
complete, and will also be written to log/ablation-validation-run<seed>.txt


Most of the arguments in the example options file are required (see the full
list with -h), but you will likely only need to change the following:

algo - the algorithm to run. If your setting for this works in SMAC, it should
work here.

execdir - the directory in which to execute each target run

experimentDir - the root directory for the experiment

sourceConfiguration -
targetConfiguration - either "DEFAULT" for the default configuration, or a
string representation of the configuration you want to use. The string
representation must be the same format as readable by SMAC. I recommend:
"-<param> '<value>' ..."

run_obj,overall_obj - the objective for each run and for aggregating all runs
for a configuration. Same available values as for SMAC.

cutoff_time - the runtime cutoff for your target algorithm, in seconds.
cutoff_length is not supported currently, just leave it set to max.

seed - the random seed to use.

useRacing - If true, use the accelerated racing-based approach. Otherwise, use
the naive brute-force ablation analysis implementation. Default is true.

paramfile = the parameter space description file, same format as for SMAC.

instance_file - list of instances in SMAC format, used for the ablation
analysis.

test_instance_file - list of instances in SMAC format, used for validation.

cli-concurrent-execution - leave as true.
cli-cores - If you want to utilize more than one of the cores on your machine,
or if your algo wrapper actually executes on, e.g., a compute cluster, set
this to how many parallel jobs you want the procedure to execute.

If you have access to an alternative Target Algorithm Execution (or TAE) plugin,
such as the UBC MySQLDBTAE or AKKA-TAE plugins, you can place it and its dependencies into the
lib/ folder and use it as normal.

If you would not like to compute the full ablation path between your source
and target configuration, you may use the "maximumAblationRounds" option to
limit the procedure to computing the first k rounds.
