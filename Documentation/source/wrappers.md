(solver-wrapper)=
# Wrapping your Algorithm

When using Sparkle for your specific projects, you will want to plug in your own algorithms into the platform. To that end, a piece of wrapper code of about ~50 lines must be written to make sure the platform is able to submit calls to your algorithm, as well as parse the output. This should in general not take longer than five minutes to write.

A template for the wrapper that connects your algorithm with Sparkle is
available at `Examples/Resources/Solvers/template/sparkle_solver_wrapper.py`.
Within this template a number of `TODO`s are indicated where you are likely to need to make changes for your specific algorithm. You can also compare the different example solvers to get an idea for what kind of changes are needed.

(solver-wrapper-file)=

## Solver Wrapper Python script

The `sparkle_solver_wrapper.py` uses a commandline dictionary to receive it inputs. This can be easily parsed using a Sparkle tool: `from sparkle.tools.solver_wrapper_parsing import parse_solver_wrapper_args`.
After parsing it with the Sparkle tools, the dictionary should always have the following values:

```
solver_dir: Path
instance: Path,
objectives: list[str],
cutoff_time: float,
seed: int
```

The solver_dir specifies the Path to the Solver directory of your algorithm, where your optional additional files can be found. This can be empty, e.g. the cwd contains your executable. The instance is the path to the instance we are going to run on. Cutoff time is the maximum amount of time your algorithm is allowed to run. Seed is the seed for this run.

When using Sparkle for algorithm configuration, this dictionary will also contain the (hyper)parameter values for your solver to use. These will all be in string format. See {ref}`Parameter configuration space <pcs-file>` for more information.

A solver wrapper should always return a dictionary by printing it, containing the following values:

```
status: Enum,
objective: any,
...
solver_call: str (optional)
```

Status can hold the following various values such as `{SUCCESS, TIMEOUT, CRASHED}`, see {ref}`SolverStatus <mod-types>` for a descriptin of the Enum. If the status is not known, reporting `SUCCESS` will allow Sparkle to continue, but may mean that Sparkle does not know when the algorithm crashed, and continues with faulty results.
To return the values of your objectives, make sure to specify them with the exact same key string as they are specified in your Settings. This key is used to map it into the platform. If you have multiple objectives, simply place each key value pair in the dictionary.
The solver_call is only used for logging purposes, to allow for easy inspection of the solver wrapper's subprocess.


(pcs-file)=

## PCS file
In order to use algorithm configuration, the algorithm configuration space must be specified in a PCS (Parameter configuration space) file.

```{note}
See the {doc}`tutorial <tutorials>` page for a walk-through on how to perform configuration with Sparkle.
```

The PCS (parameter configuration space) format is used to pass the possible parameter ranges of an algorithm to Sparkle in a `.pcs` file. For an example see e.g. `Examples/Resources/Solvers/PbO-CCSAT-Generic/PbO-CCSAT-params_test.pcs`.

In this file you should enter all configurable parameters of your algorithm. Note that parameters such as the random seed used by the
algorithm should not be configured and therefore should also not be included in the PCS file.
