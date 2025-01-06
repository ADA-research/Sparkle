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

The solver directory should contain the solver executable, the `sparkle_solver_wrapper` wrapper, and a `.pcs` file describing the configurable parameters. In this example, we are running a SAT solver, and we can add the argument for a solution verifier to check each solution presented by the solver, and update its status acccordingly.

```bash
sparkle add_solver Examples/Resources/Solvers/PbO-CCSAT-Generic/ --solution-verifier SATVerifier
```

If needed solvers can also include additional files or scripts in their directory, but keeping additional files to a minimum speeds up copying.

### Configure the solver

To perform configuration on the solver to obtain a target configuration we run:

```bash
sparkle configure_solver --solver Solvers/PbO-CCSAT-Generic/ --instance-set-train Instances/PTN/ --instance-set-test Instances/PTN2
```

This step should take about ~10 minutes, although it is of course very cluster / slurm settings dependant. If you are using the default settings, this will use SMAC2 as configurator. If you wish to run with a different configurator, we also supply default settings for the other configurators for this scenario. You can simply change the configurator name in `sparkle_settings.ini` under the `general` section.

### Generate a report

We have to wait for the algorithm configuration to be completed, to get live updates on your terminal we can simply run:

```bash
sparkle jobs
```

And now we can generate a report detailing the results on the training (and optionally testing) set. This includes the experimental procedure and performance information; this will be located in `Output/Configuration/Analysis/`. Note that you may get the warning that not all solvers have been run yet: Sometimes an algorithm call may crash and can easily be restarted by sparkle by running `sparkle run solvers`.

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
sparkle jobs
```

Generate a report including ablation, and as before the results on the train (and optionally test) set, the experimental procedure and performance information; this will be located in a `Configuration_Reports/` subdirectory for the solver, training set, and optionally test set like `PbO-CCSAT-Generic_PTN/Sparkle-latex-generator-for-configuration/`

```bash
sparkle generate_report
```

The ablation section can be suppressed with `--no-ablation` 

### Run configured solver

#### Run configured solver on a single instance

Now that we have a configured solver, we can run it on a single instance to get a result. We do not have to specify which solver, as we only added one to Sparkle in this example. By specifying an instance set after `--best-configuration`, Sparkle will only consider configurations found for this instance set.

```bash
sparkle run_solvers --best-configuration PTN --instance Examples/Resources/Instances/PTN2/Ptn-7824-b20.cnf --run-on local
```

#### Run configured solver on an instance directory

It is also possible to run a configured solver directly on an entire directory.

```bash
sparkle run_solvers --best-configuration PTN --instance Examples/Resources/Instances/PTN2
```