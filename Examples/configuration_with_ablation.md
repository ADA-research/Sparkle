### Load the solver and instances into Sparkle

Initialise the Sparkle platform

`Commands/initialise.py`

Add train, and optionally test, instances (in CNF format) in a given directory, without running solvers or feature extractors yet

`Commands/add_instances.py --run-solver-later --run-extractor-later Examples/Resources/Instances/PTN/`
`Commands/add_instances.py --run-solver-later --run-extractor-later Examples/Resources/Instances/PTN2/`

Add solvers with a wrapper containing the executable name of the solver and parameter configuration space (.pcs) file, without running the solvers yet

(the directory should contain both the executable and the wrapper)

`Commands/add_solver.py --run-solver-later --deterministic 0 Examples/Resources/Solvers/PbO-CCSAT-Generic/`


### Perform configuration on the solver to obtain a target configuration

Run the portfolio selector on a single testing instance; the result will be printed to the command line

`Commands/configure_solver.py --solver Solvers/PbO-CCSAT-Generic/ --instance-set-train Instances/PTN`

### Run parameter importance between the default configuration (from the .pcs file) and the parameters found with configuration using ablation.

Run ablation where the path is created using the train instances and the validation of the parameter importance is validated by the test set

`./Commands/run_ablation.py --solver Solvers/PbO-CCSAT-Generic/ --instance-set-train Instances/PTN --instance-set-test Instances/PTN2/`

At the same time you can validate the performance of the best found parameter configuration with

`./Commands/validate_configured_vs_default.py --solver Solvers/PbO-CCSAT-Generic/ --instance-set-train Instances/PTN --instance-set-test Instances/PTN2/`

Generate a report detailing the results on the train (and test) set including ablation, and as before the experimental procedure and performance information; this will be located at `Configuration_Reports/PbO-CCSAT-Generic_PTN/Sparkle-latex-generator-for-configuration/`

`Commands/generate_report_for_configuration.py  --solver Solvers/PbO-CCSAT-Generic/ --instance-set-train Instances/PTN/ --instance-set-test Instances/PTN2/`

The ablation section can be supressed with `--no-ablation` 

### Immediate ablation and validatation after configuration

By adding `--ablation` and/or `--validation` to `configure_solver.py`, ablation and respectivelly validation will run directly after the configuration has finished. 
`Commands/configure_solver.py --solver Solvers/PbO-CCSAT-Generic/ --instance-set-train Instances/PTN --ablation --validation`

There is no need to execute `run_ablation.py` and/or `validate_configured_vs_default.py` when these flags are given afterwards

