# Use Sparkle for algorithm configuration

These steps can also be found as a Bash script in `Examples/configuration.sh`

## Initialise the Sparkle platform

`Commands/initialise.py`

## Add instances

Add train, and optionally test, instances (in this case in CNF format) in a given directory, without running solvers or feature extractors yet

`Commands/add_instances.py Examples/Resources/Instances/PTN/`

`Commands/add_instances.py Examples/Resources/Instances/PTN2/`

## Add a configurable solver

Add a configurable solver (here for SAT solving) with a wrapper containing the executable name of the solver and a string of command line parameters, without running the solver yet

The solver directory should contain the solver executable, the `sparkle_smac_wrapper.py` wrapper, and a `.pcs` file describing the configurable parameters

`Commands/add_solver.py --deterministic 0 Examples/Resources/Solvers/PbO-CCSAT-Generic/`

If needed solvers can also include additional files or scripts in their directory, but keeping additional files to a minimum speeds up copying.

## Configure the solver

Perform configuration on the solver to obtain a target configuration

`Commands/configure_solver.py --solver Solvers/PbO-CCSAT-Generic/ --instance-set-train Instances/PTN/`

## Validate the configuration

To make sure configuration is completed before running validation you can use the `sparkle_wait` command

`Commands/sparkle_wait.py`

Validate the performance of the best found parameter configuration. The test set is optional.

`Commands/validate_configured_vs_default.py --solver Solvers/PbO-CCSAT-Generic/ --instance-set-train Instances/PTN/ --instance-set-test Instances/PTN2/`

## Generate a report

Wait for validation to be completed

`Commands/sparkle_wait.py`

Generate a report detailing the results on the training (and optionally testing) set. This includes the experimental procedure and performance information; this will be located in a `Configuration_Reports/` subdirectory for the solver, training set, and optionally test set like `PbO-CCSAT-Generic_PTN/Sparkle-latex-generator-for-configuration/`

`Commands/generate_report.py`

By default the `generate_report` command will create a report for the most recent solver and instance set(s). To generate a report for older solver-instance set combinations, the desired solver can be specified with `--solver Solvers/PbO-CCSAT-Generic/`, the training instance set with `--instance-set-train Instances/PTN/`, and the testing instance set with `--instance-set-test Instances/PTN2/`.

## Run ablation to determine parameter importance based on default (from the `.pcs` file) and configured parameters

### Run ablation

Run ablation using the training instances and validate the parameter importance with the test set

`Commands/run_ablation.py --solver Solvers/PbO-CCSAT-Generic/ --instance-set-train Instances/PTN/ --instance-set-test Instances/PTN2/`

### Generate a report

Wait for ablation to be completed

`Commands/sparkle_wait.py`

Generate a report including ablation, and as before the results on the train (and optionally test) set, the experimental procedure and performance information; this will be located in a `Configuration_Reports/` subdirectory for the solver, training set, and optionally test set like `PbO-CCSAT-Generic_PTN/Sparkle-latex-generator-for-configuration/`

`Commands/generate_report.py`

The ablation section can be suppressed with `--no-ablation` 

## Immediate ablation and validation after configuration

By adding `--ablation` and/or `--validate` to the `configure_solver.py` command, ablation and respectively validation will run directly after the configuration is finished.

There is no need to execute `run_ablation.py` and/or `validate_configured_vs_default.py` when these flags are given with the `configure_solver.py` command

### Training set only

`Commands/configure_solver.py --solver Solvers/PbO-CCSAT-Generic/ --instance-set-train Instances/PTN/ --ablation --validate`

### Training and testing sets

Wait for the previous example to be completed

`Commands/sparkle_wait.py`

`Commands/configure_solver.py --solver Solvers/PbO-CCSAT-Generic/ --instance-set-train Instances/PTN/ --instance-set-test Instances/PTN2/ --ablation --validate`

