# Use Sparkle to run a configured solver

These steps can also be found as a Bash script in `Examples/configured_solver.sh` The first few steps overlap with the example from configuration, as we need a configured solver first.

## Initialise the Sparkle platform

`Commands/initialise.py`

## Add instances

Adding train instances (Here in CNF format) in a given directory.

`Commands/add_instances.py Examples/Resources/Instances/PTN/`

## Add the solver

Add a configurable solver (SAT solver in this case) with a wrapper containing the executable name of the solver.

`Commands/add_solver.py --deterministic 0 Examples/Resources/Solvers/PbO-CCSAT-Generic/`

## Configure the solver

Perform configuration on the solver to obtain a target configuration

`Commands/configure_solver.py --solver Solvers/PbO-CCSAT-Generic/ --instance-set-train Instances/PTN/`

### Wait for the solver configuration to be done

`Commands/sparkle_wait.py`

## Run configured solver on a single instance

Now that we have a configured solver, we can run it on a single instance to get a result.

`Commands/run_configured_solver.py Examples/Resources/Instances/PTN2/Ptn-7824-b20.cnf`

## Run configured solver on an instance directory
It is also possible to run a configured solver directly on an entire directory of instances in parallel.

`Commands/run_configured_solver.py Examples/Resources/Instances/PTN2 --parallel`