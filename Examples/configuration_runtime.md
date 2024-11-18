## Algorithm Runtime Configuration

These steps can also be found as a Bash script in `Examples/configuration.sh`

### Initialise the Sparkle platform

```bash
sparkle initialise
```

### Add instances

Add train, and optionally test, instances (in this case in CNF format) in a given directory, without running solvers or feature extractors yet

```bash
sparkle add_instances Examples/Resources/Instances/PTN/
sparkle add_instances Examples/Resources/Instances/PTN2/
```

### Add a configurable solver

Add a configurable solver (here for SAT solving) with a wrapper containing the executable name of the solver and a string of command line parameters, without running the solver yet

The solver directory should contain the solver executable, the `sparkle_solver_wrapper` wrapper, and a `.pcs` file describing the configurable parameters

```bash
sparkle add_solver Examples/Resources/Solvers/PbO-CCSAT-Generic/
```

If needed solvers can also include additional files or scripts in their directory, but keeping additional files to a minimum speeds up copying.

### Configure the solver

To perform configuration on the solver to obtain a target configuration we run:

```bash
sparkle configure_solver --solver Solvers/PbO-CCSAT-Generic/ --instance-set-train Instances/PTN/
```

This step should take about ~10 minutes, although it is of course very cluster / slurm settings dependant. If you are using the default settings, this will use SMAC2 as configurator. If you wish to run with a different configurator, we also supply default settings for the other configurators for this scenario. You can simply change the configurator name in `sparkle_settings.ini` under the `general` section.

### Validate the configuration

To make sure configuration is completed before running validation you can use the `wait` command

```bash
sparkle wait
```

Now we can validate the performance of the best found parameter configuration against the default configuration specified in the PCS file. The test set is optional.

```bash
sparkle validate_configured_vs_default --solver Solvers/PbO-CCSAT-Generic/ --instance-set-train Instances/PTN/ --instance-set-test Instances/PTN2/
```

### Generate a report

Wait for validation to be completed

```bash
sparkle wait
```

Generate a report detailing the results on the training (and optionally testing) set. This includes the experimental procedure and performance information; this will be located in a `Configuration_Reports/` subdirectory for the solver, training set, and optionally test set like `PbO-CCSAT-Generic_PTN/Sparkle-latex-generator-for-configuration/`

```bash
sparkle generate_report
```

By default the `generate_report` command will create a report for the most recent solver and instance set(s). To generate a report for older solver-instance set combinations, the desired solver can be specified with `--solver Solvers/PbO-CCSAT-Generic/`, the training instance set with `--instance-set-train Instances/PTN/`, and the testing instance set with `--instance-set-test Instances/PTN2/`.

### Run ablation

We can run ablation to determine parameter importance based on default (from the `.pcs` file) and configured parameters.
To run ablation using the training instances and validate the parameter importance with the test set

```bash
sparkle run_ablation --solver Solvers/PbO-CCSAT-Generic/ --instance-set-train Instances/PTN/ --instance-set-test Instances/PTN2/
```

#### Generate a report

Wait for ablation to be completed

```bash
sparkle wait
```

Generate a report including ablation, and as before the results on the train (and optionally test) set, the experimental procedure and performance information; this will be located in a `Configuration_Reports/` subdirectory for the solver, training set, and optionally test set like `PbO-CCSAT-Generic_PTN/Sparkle-latex-generator-for-configuration/`

```bash
sparkle generate_report
```

The ablation section can be suppressed with `--no-ablation` 

### Run configured solver

#### Run configured solver on a single instance

Now that we have a configured solver, we can run it on a single instance to get a result.

```bash
sparkle run_configured_solver Examples/Resources/Instances/PTN2/Ptn-7824-b20.cnf
```

#### Run configured solver on an instance directory

It is also possible to run a configured solver directly on an entire directory.

```bash
sparkle run_configured_solver Examples/Resources/Instances/PTN2
```