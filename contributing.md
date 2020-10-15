Every command should write to a general log file when executed as:
<timestamp> <command_name> <command_arguments> <reference_to_output>

<reference_to_output> should be a short text file listing the different outputs (logs, data, sparkle files, ...) and brief explanations.

Execution (e.g. of srun/sbatch scripts) should happen in TMP as much as possible. When execution finishes successfully logs and data should be moved to their appropriate directories (e.g. LOG/Configuration and DATA/Performance).

To simplify debugging old logs that do not need to be stored should be deleted only once a command is executed again. For instance the configure command would start by deleting the logs from the previous configuration run, rather than deleting the logs immediately after generating them.

The /LOG/ directory should be organised as follows:
LOG/
	Configuration/
		<solver_instanceSet>/
	Feature_Extraction/
		<extractor_instanceSet>/
	Performance_Computation/
		<solver_instanceSet>/
	Selection/
		...
	Validation/
		<solver_trainingSet_testingSet>/
			configured_train/
			configured_test/
			default_train/
			default_test/
	...

The /Data/ and /Reports/ directories should be organised similarly
