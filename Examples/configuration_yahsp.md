### Use Sparkle for algorithm configuration

#### Initialise the Sparkle platform

`Commands/initialise.py`

#### Add instances

Add train, and optionally test, instances (in this case for the AI planning) in a given directory, without running solvers or feature extractors yet

`Commands/add_instances.py --run-solver-later --run-extractor-later Examples/Resources/Instances/Depots_train_few/`
`Commands/add_instances.py --run-solver-later --run-extractor-later Examples/Resources/Instances/Depots_test_few/`

#### Add a configurable solver

Add a configurable solver (here for vehicle routing) with a wrapper containing the executable name of the solver and a string of command line parameters, without running the solver yet

The solver directory should contain the solver executable, the `sparkle_smac_wrapper.py` wrapper, and a `.pcs` file describing the configurable parameters

*This specific problem/solver requires additional files in its directory:* `generate_domain_file.py`, `HEADER`, `OP1`, `OP2`, `OP3`, `OP4`, `OP5`, `PREDICATES`

`Commands/add_solver.py --run-solver-later --deterministic 0 Examples/Resources/Solvers/Yahsp3/`

#### Configure the solver

Perform configuration on the solver to obtain a target configuration.

`Commands/configure_solver.py --solver Solvers/Yahsp3/ --instance-set-train Instances/Depots_train_few/`

#### Validate the configuration

Validate the performance of the best found parameter configuration. The test set is optional.

`./Commands/validate_configured_vs_default.py --solver Solvers/Yahsp3/ --instance-set-train Instances/Depots_train_few/ --instance-set-test Instances/Depots_test_few/`

#### Generate a report

Generate a report detailing the results on the training (and optionally testing) set. This includes the experimental procedure and performance information; this will be located in a `Configuration_Reports/` subdirectory for the solver, training set, and optionally test set like `Yahsp3_Depots_train_few/Sparkle-latex-generator-for-configuration/`.

`Commands/generate_report.py`

By default the `generate_report` command will create a report for the most recent solver and instance set(s). To generate a report for older solver-instance set combinations, the desired solver can be specified with `--solver Solvers/Yahsp3/`, the training instance set with `--instance-set-train Instances/Depots_train_few/`, and the testing instance set with `--instance-set-test Instances/Depots_test_few/`.

