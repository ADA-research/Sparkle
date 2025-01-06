# Commands

(quick-execute-commands)=

## Executing commands

Executing commands in Sparkle is as simple as running them terminal for example:

```
sparkle initialise
```

Do note that when running on a cluster additional arguments may be
needed, for instance under the Slurm workload manager. All CLI entries are placed in
the sparkle package `sparkle/CLI/$COMMANDNAME$.py` the above command would change to
something like:

```
srun -N1 -n1 -c1 path/to/package/sparkle/CLI/initialise.py
```

In the `Examples/` directory a number of common command sequences are given. For instance, for configuration with specified training and
testing sets see e.g. `Examples/configuration_runtime.sh` for an example of a sequence of commands to execute. Note that some command run in the background and need time to complete before the next command is executed. To see whether a command is still running the `jobs` command can be used.

In the `Output/` directory paths to generated scripts and logs are gathered per executed command.

```{note}
When typing a sparkle command name that consists of multiple words, both spaces and underscores are accepted as seperators.
```

## List of Commands

Currently the commands below are available in Sparkle (listed alphabetically). Every command can be called with the `–help` option to get a description of the required arguments and other options.


```{include} commandlist.md
```

```{note}
Arguments in \[square brackets\] are optional, arguments without brackets
are mandatory. Input in \<chevrons> indicate required text input, {curly
brackets} indicate a set of inputs to choose from.
```

```{include} commandsautoprogram.md
```