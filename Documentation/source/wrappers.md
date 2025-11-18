(solver-wrapper)=
# Wrapping your Algorithm

When using Sparkle for your specific projects, you will want to plug in your own algorithms into the platform. To that end, a piece of wrapper code of about ~50 lines must be written to make sure the platform is able to submit calls to your algorithm, as well as parse the output. This should in general not take longer than five minutes to write. An extensive description on the file itself is given in the first subsection of this page.

As a good starting point for a Bash wrapper, you can call the `wrap` command in sparkle like so;

```bash
sparkle wrap solver path/to/my/solver path/to/my/solver/executable --generate-pcs 
```

This will take the wrapper template and write it for you in your solver directory with the executable variable in place. Note that `path/to/my/solver/executable` can also be relative, e.g. `executable` as second argument would also suffice. The `--generate-pcs` will open an interactive session that attempts to extract all arguments from your `executable` by running it with `--help`. In this interactive session you can choose which parameters should be added, with which type and default value. This will then create a ConfigSpace YAML file, which you can easily edit afterwards for more detailed settings, such as adding forbidden clauses or conditional parameters.

Alternatively, the raw templates for the wrapper that connects your algorithm with Sparkle is available at `Examples/Resources/Solvers/template/` where a [Python](https://github.com/ADA-research/Sparkle/blob/main/Examples/Resources/Solvers/template/sparkle_solver_wrapper.py) and [Bash](https://github.com/ADA-research/Sparkle/blob/main/Examples/Resources/Solvers/template/sparkle_solver_wrapper.sh) version are given. In this template a few steps need to be filled in with your own algorithm, such as setting the name of your executable and parsing its output. You can also compare the different example solvers in this directory to get an idea for what kind of changes are needed.

```{note}
We recommend writing your wrapper using the Bash template, as it offers the fastest execution time, unless your solver itself is written in Python.
```

It is important to Sparkle that the last line of output is a dictionary that Sparkle can process. In the example scripts there are details on how to handle Kill Signals, s.t. you can make sure that in any call your wrapper will output a specific structure.

(solver-wrapper-file)=

## Solver Wrapper Python script

The `sparkle_solver_wrapper` receives via commandline a dictionary as its inputs. This can be easily parsed in Python using a Sparkle tool: `from sparkle.tools.solver_wrapper_parsing import parse_solver_wrapper_args`. After parsing it with the Sparkle tools, the dictionary should always have the following values:

```
solver_dir: Path
instance: Path,
objectives: list[str],
cutoff_time: float,
seed: int
```

The solver_dir specifies the Path to the Solver directory of your algorithm, where your optional additional files can be found. This can be empty, e.g. the cwd contains all your extra files. This can be useful when your algorithm is an executable that you need to run from the wrapper. The instance is the path to the instance we are going to run on. Cutoff time is the maximum amount of time your algorithm is allowed to run, which you set yourself in the `sparkle_settings.ini` under section `general` as option `solver_cutoff_time`. Seed is the seed for this run.

When using Sparkle for algorithm configuration, this dictionary will also contain the (hyper)parameter values for your solver to use. These will all be in string format. See {ref}`Parameter configuration space <pcs-file>` for more information.

A solver wrapper should always return a dictionary by printing it, containing the following values:

```
status: Enum,
objective: any,
...
solver_call: str (optional)
```

Status can hold the following various values such as `{SUCCESS, TIMEOUT, CRASHED}`, see {ref}`SolverStatus <mod-types>` for a description of the Enum. If the status is not known, reporting `SUCCESS` will allow Sparkle to continue, but may mean that Sparkle does not know when the algorithm crashed, and continues with faulty results.
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

```{warning}
Although you can specify _default_ values for your parameters, it is not guaranteed each parameter will always be present in the input dictionary. It is therefore strongly encouraged to have the default/back up values available for each parameter in your wrapper.
```

## Checking your Solver

Once you feel all modifications needed have been done, you might want to test if everything is plugged into Sparkle correctly. To do so, you can run `sparkle check`. Here you can specify what you want to check (in this case `solver`, but you can use it for instance sets or feature extractors as well) and test your solver with an example instance as well. We recommend an easy instance that runs quickly. An example call:

```bash
sparkle check solver my_solvers/solverA my_instances --cutoff 60 -seed 42
```

Note that only the path to your Solver is required, all other arguments are optional (but recommended as it allows for more checks). If a PCS file is present, the check function will also generate a random configuration to test with.
