# Platform

## File structure

The platform automatically generates a file structure for both input and output upon initialisation.

(dir-instances)=

### Instance directory

The instance directory has the following structure:

```
Instances/
  Example_Instance_Set/
    instance_a.cnf
    instance_b.cnf
    ...        ...
    instance_z.cnf
```

Each directory under the Instances directory represents an `Instance Set` and each file is considered an instance. Note that if your dataset is a single file, it will be considered a single instance in the set.

For instances consisting of multiple files one additional file called `instances.csv` should be included in the `Example_Instance_Set` directory, describing which files together form an instance. The format is a single instance per line with each file separated by a space, as shown below.

```
instance_name_a instance_a_part_one.abc ... instance_a_part_n.xyz
instance_name_b instance_b_part_one.abc ... instance_b_part_n.xyz
...                     ...
instance_name_z instance_z_part_one.abc ... instance_z_part_n.xyz
```

(dir-solvers)=

### Solver Directory

The solver directory has the following structure:

```
Solver/
  Example_Solver/
    sparkle_solver_wrapper.py
    parameters.pcs
    ...
```

The `sparkle_solver_wrapper.py` is a wrapper that Sparkle should call to run the solver with specific settings, and then returns a result for the configurator. In `parameters.pcs` the configurable parameters are described in the PCS format. Finally, when importing your Solver into Sparkle, a binary executable of the runsolver tool `runsolver` is added. This allows Sparkle to make fair time and computational cost measurements for all configuration experiments.

### The output directory

```{note}
This section describes a desirable behaviour but has not been implemented fully yet.
```

The output directory is located at the root of the Sparkle directory. Its structure is as follows:

```
Output/
  Logs/
    commandname_timestamp/
        logs
  Configuration/
    configurator/
        Raw_Data/
            related files
    Analysis/
  Parallel_Portfolio/
    Raw_Data/
        related files
    Analysis/
  Selection/
    selector/
        solver_scenario/
            related files
    Analysis/
```

The `Logs` directory should contain the history of commands and their output such that one can easily know what has been done in which order and find enough pointers to debug unwanted behaviour.

Other directories are cut into two subdirectories: `Raw_Data` contains the data produced by the main command, often time consuming to generate, handle with care; `Analysis` contains information extracted from the raw data, easy to generate, plots and reports.

For each type of task run by Sparkle, the `related files` differ. The aim is always to have all required files for reproducibility. A copy of the sparkle configuration file at the time of the run and of all files relevant to the run, a copy of any log or error file that could help with debugging or a link to it, and the output of the executed task.

*For configuration* the configuration trajectory if available, the training and testing sets, the default configuration and the final found configuration. The performance of those will be in the Analysis folder.

*For parallel portfolio* the resulting portfolio and its components. The performance of the portfolio will be in the Analysis folder.

*For selection* the algorithms and their performance on the training set, the model(s) generated if available and the resulting selector. The performance evaluation of the selector will be in the Analysis folder.

*For analysis* a link to the folder on which the analysis was performed (configuration, portfolio or selection), the performance evaluation from it and the report if it was generated.


(settings)=
## Platform Settings

Most settings can be controlled through the `Settings` directory, specifically the `Settings/sparkle_settings.ini` file. Possible settings are summarised per category in {numref}`settings-details`. For any settings that are not provided the defaults will be used. Meaning, in the extreme case, that if the settings file is empty (and nothing is set through the command line) everything will run with default values.

For convenience after every command `Settings/latest.ini` is written with the used settings. Here any overrides by commandline arguments are reflected. This can, for instance, provide the same settings to the next command in a chain. E.g. for `validate_configured_vs_default` after `configure_solver`. The used settings are also recorded in the relevant `Output/` subdirectory. Note that when writing settings Sparkle always uses the name, and not an alias.

```{note}
When overriding settings in `sparkle_settings.ini` with the commandline arguments, this is considered as 'temporary' and only denoted in the latest_settings, but does not actually affect the values in sparkle_settings.ini
```

### Example `sparkle_settings.ini`

This is a short example to show the format.

```
[general]
objective = RUNTIME
target_cutoff_time = 60

[configuration]
number_of_runs = 25

[slurm]
number_of_runs_in_parallel = 25
```

When initialising a new platform, the user is provided with a default settings.ini, which can be viewed [here](https://raw.githubusercontent.com/ADA-research/Sparkle/main/sparkle/Components/sparkle_settings.ini).

(sparkle-objective)=
### Sparkle Objectives
To define an objective for your algorithms, you can define them in the `general` section of your `Settings.ini` like the following:

```
[general]
objective = PAR10,loss,accuracy:max
```

In the above example we have defined three objectives: Penalised Average Runtime, the loss function value of our algorithm on the task, and the accuracy of our algorithm on the task. Note that objectives are by default assumed to be _minimised_ and we must therefore specify **accuracy_:max_** to clarifiy this. The platform predefines for the user three objectives: cpu time, wallclock time and memory. These objectives will always recorded next to whatever the user may choose.

```{note}
Although the Platform supports multiple objectives to be registered for any Solver, not all used components, such as SMAC and Ablation Analysis, support Multi-Objective optimisation. In any such case, the first defined objective is considered the most important and used in these situations
```

Moreover, when aggregating an objective over various dimensions, Sparkle assumes the following:

- When aggregating multiple Solvers (Algorithms), we aggregate by taking the minimum/maximum value.
- When aggregating multiple runs on the same instances, we aggregate by taking the mean.
- When aggregating multiple instances, we aggregate by taking the mean.

It is possible to redefine these attributes for your specific objective. The platform looks for a file called `objective.py` in your Settings directory of the platform, and reads your own object definitions, which can overwrite existing definitions in the library. E.g. when creating an objective definition that already exists in the library, the user definiton simply overrules the library definition. Note that there are a few constraints and details:

- The objective must inherit from the `SparkleObjective` class
- The objective can be parametrised by an integer, such as `PAR` followed by `10` is interpreted as instantiating the `PAR` class with argument `10`
- The classnames are constrained to the format of alphabetical letters followed by numericals

(settings-details)=
### Names and possible values

**\[general\]**

`objective`
> aliases: `objective`
>
> values: `str`, comma seperated for multiple
> description: The type of objectives Sparkle considers, see {ref}`Sparkle Objective section <sparkle-objective>` for more. 

`target_cutoff_time`
> aliases: `smac_each_run_cutoff_time`, `cutoff_time_each_performance_computation`
>
> values: integer
>
> description: The time a solver is allowed to run before it is terminated.

`extractor_cutoff_time`
> aliases: `cutoff_time_each_feature_computation`
>
> values: integer
>
> description: The time a feature extractor is allowed to run before it is terminated. In case of multiple feature extractors this budget is divided equally.

`solution_verifier`
> aliases: N/A
>
> values: `{NONE, SAT}`
>
> note: Only available for SAT solving.

**\[configuration\]**

`wallclock_time`
> aliases: `smac_whole_time_budget`
>
> values: integer
>
> description: The wallclock time one configuration run is allowed to use for finding configurations.

`cpu_time`
> aliases: `smac_cpu_time_budget`
>
> values: integer
>
> description: The cpu time one configuration run is allowed to use for finding configurations.

`solver_calls`
> aliases: `smac_solver_calls_budget`
>
> values: integer
>
> description: The number of solver calls one configuration run is allowed to use for finding configurations.

`number_of_runs`
> aliases: `num_of_smac_runs`
>
> values: integer
>
> description: The number of separate configurations runs.

**\[smac\]**

`target_cutoff_length`
> aliases: `smac_each_run_cutoff_length`
>
> values: `{max}` (other values: whatever is allowed by SMAC)

**\[ablation\]**

`racing`
> aliases: `ablation_racing`
>
> values: boolean
>
> description: Use racing when performing the ablation analysis between the default and configured parameters

**\[slurm\]**

`number_of_runs_in_parallel`
> aliases: `smac_run_obj`
>
> values: integer
>
> description: The number of configuration runs that can run in parallel. 

`max_parallel_runs_per_node`
> aliases: `clis_per_node`
>
> values: integer
>
> note: Not really a Slurm option, will likely be moved to another section.
>
> description: The number of parallel processes that can be run on one compute node. In case a node has 32 cores and each solver uses 2 cores, the `max_parallel_runs_per_node` is at most 16.

### Priorities

Sparkle has a large flexibility with passing along settings. Settings provided through different channels have different priorities
as follows:

- Default –- Default values will be overwritten if a value is given
  through any other mechanism;
- File –- Settings form the `Settings/sparkle_settings.ini` overwrite
  default values, but are overwritten by settings given through the
  command line;
- Command line Settings file -– Settings files provided through the command line,
  overwrite default values and other settings files.
- Command line –- Settings given through the command line overwrite all
  other settings, including settings files provided through the command
  line.

## Slurm

Slurm settings can be specified in the `Settings/settings.ini` file. Any setting in the Slurm section not internally recognised by Sparkle will be added to the `sbatch` or `srun` calls. It is advised to overwrite the default settings specific to your cluster, such as the option "--partition" with a valid value on your cluster. Also, you might have to adapt the default "--mem-per-cpu" value to your system. For example, your Slurm section in the `settings.ini` could look like:

```
[slurm]
partition = CPU
mem-per-cpu = 6000
...
time = 25:00
```

**Discouraged options**
Currently these settings are inserted *as is* in any Slurm calls done by Sparkle. This means that any options exclusive to one or the other currently should not be used. The options below are exclusive to `sbatch` and are thus discouraged:

- `-–array`
- `-–clusters`
- `-–wrap`

The options below are exclusive to `srun` and are thus discouraged:

- `-–label`

## Required packages

Other software used by Sparkle:

- `pdflatex`
- `latex`
- `bibtex`