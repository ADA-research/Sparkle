# Configurators

Sparkle offers several configurators to use for Algorithm Configuration. Although they come with automatic installations and various default settings, you might need to set up a few details for your specific system and algorithm or data set to make sure everything works as intended.

## Parameter Configuration Space

In order to use configurators, they require Parameter Configuration Space (PCS) definitions to explore the space of configurations or hyperparameter values. These definitions usually are made of three parts:

1. Parameter definitions, usually in the types of integer, real, categorical and ordinal. Defining the range (And whether its log scale for numerical) and default value is usually required.
2. Parameter conditions, for parameters that are only active based on the values of other parameters.
3. Forbidden parameter combinations, which are usually equations of parameters that you know will not work (based on the problem or algorithm definition for example)

Each configurator has its own file layout and possibilities. Luckily you do not have to provide a PCS for each one: You can simply provide one file that ends with .pcs and Sparkle will automatically convert it to a [ConfigurationSpace](https://automl.github.io/ConfigSpace/latest/) object and parse it to all other formats through PCSConverter. Do note that certain limitations are present for this method as the ConfigSpace object does not cover all expresivity of each Configurator. In each section below, details and limitations of the PCS are clarified per configurator.

## SMAC2

Sequential Model-Based Optimization for General Algorithm Configuration[[1]](#1), or [SMAC]((https://www.cs.ubc.ca/labs/algorithms/Projects/SMAC)) for short is a Java based algorithm configurator. *Note that this the second version, and not SMAC3 the Python version. For SMAC3 see below*. The original documentation of the configurator can be found [here](https://www.cs.ubc.ca/labs/algorithms/Projects/SMAC/v2.10.03/manual.pdf).

```{note}
SMAC2 is written in Java and therefore requires Java to be installed in your environment. The current tested version in Sparkle is 1.8.0_402
```

### Budget

SMAC2 receives it budget in terms of `solver_calls`, which specifies the maximum amount of times the target solver (e.g. your algorithm) may be run on a certain instance, or through `cpu_time` or `wallclock_time`. Note that in the case of using time as a budget, not only the solver time measurement is used for the budget but also that of SMAC itself. If you want only the execution time of the algorithm to be used for the budget, set `use_cpu_time_in_tunertime` to `False`.

### PCS

The documentation of SMAC2 states that (complex) formulae are supported in their expressions. However, this is not supported by the PCSConverter and statements such as `log(x) > 1`, `(x^2 + y^2 > z^2)` or even `a * 2 > 5` will be skipped.

## SMAC3

The Python version of Sequantial Model-Based Optimization for General Algorithm Configuration[[2]](#2), or [SMAC3](https://github.com/automl/SMAC3) for short. The original documentation can be found [here](https://automl.github.io/SMAC3/). 

### Budget

SMAC3 can be budgetted in terms of `solver_calls`, which specifies the maximum amount of times the target solver (e.g. your algorithm) may be run on a certain instance, but also through `walltime_limit` or `cputime_limit`. Not that the time limits only consider the budget in terms of time used by your solver, and not time used by the configurator. The time used by your solver is timed in Sparkle by RunSolver and directly communicated to SMAC3 to ensure comparibility cross platform. SMAC3 also offers target solver limitations in terms of time and memory, but this is not available in Sparkle by design, as this would cause SMAC3 to wrap our target algorithm call by Pynisher. However, RunSolver is more accurate in its measurements and to avoid any interference between the two resource management tools, this is disabled.

```{warning}
Although misleading, SMAC3 does currently not actually support CPU time: The budgets are deducted by a single 'time' variable, and currently Sparkle communicates measured CPU time for fairness. It is planned to separate these variables, such that the budgets are actually different.
```

### PCS

SMAC3 uses direct ConfigSpace objects in their procedure.

## IRACE

Iterated Racing for Automatic Algorithm Configuration[[3]](#3), or [IRACE](https://mlopez-ibanez.github.io/irace/) for short is an R based algorithm configurator. The full documentation of the configurator can be found [here](https://cran.r-project.org/web/packages/irace/vignettes/irace-package.pdf).

IRACE offers many parameters that can be set, but also automatically computed in accordance with their paper[[2]](#2) and we recommend not deviating from those formulae as it may result in unexpected behaviour.

```{note}
IRACE is written in R and therefore requires R to be installed in your environment. The current tested version in Sparkle is R 4.3.1
```

### Budget

In order to set a budget, IRACE offers two mutually exclusive parameters: `MaxExperiments` (Also known in Sparkle as `solver_calls`) and `MaxTime`.

```{note}
Since these two budgets are mutually exclusive, IRACE won't start if both are set. To avoid this, Sparkle will default to MaxExperiments.
```

#### MaxExperiments

The `MaxExperiments` parameter can be set through the `irace` section of the `sparkle_settings.ini` with the key word `max_experiments`. The user can fill in any value, but do note that IRACE pre-computes a minimum budget at runtime. Thus, setting a too low budget can cause the configurator to immediatly exit with an error.

```{note}
This parameter can also be set through `solver_calls` in the configuration section, but this value will be ignored if the IRACE section specifies either `max_time` or `max_experiments`
```

#### MaxTime

The MaxTime parameter specifies the budget in terms of maximum runtime of the target algorithm (e.g. your Solver in the Sparkle Platform). Sparkle measures the time spend of your solver using RunSolver, and passes the **CPU** time to IRACE to determine its spend budget. IRACE also tries to determine how much budget it has for the first run using the `budgetEstimation` parameter, which is by default set to 2%. Sparkle will attempt to recompute this based on `solver_cutoff_time` (The time limit of your Solver in each call) and the `max_time` budget as ```solver_cutoff_time``` / ```max_time```, but only if the fraction is less than 1.0. **Note** that IRACE differs from SMAC2 in its time usage calculations, as it does not include the time used by IRACE itself to determine how much budget is left. See the SMAC2 section on how this can be changed.

### PCS

IRACE supports complex conditional statements in their PCS which, like SMAC2, are not supported currently by PCSConverter.

## ParamILS

Parameter Iterated Local Search[[4]](#4) or [ParamILS](https://www.cs.ubc.ca/labs/algorithms/Projects/ParamILS/) for short is an originally Ruby based algorithm configurator that has been ported to a multi-objective version written in Java by [Aymeric Blot](http://www0.cs.ucl.ac.uk/staff/a.blot/software/). The original documentation can be found [here](https://www.cs.ubc.ca/labs/algorithms/Projects/ParamILS/papers/09-JAIR-ParamILS.pdf) and the documentation on the adaptation [here](http://www0.cs.ucl.ac.uk/staff/a.blot/files/artefacts/paramils_quickstart.pdf).

```note
ParamILS does *not* directly support floating point ranges: If you let Sparkle automatically convert your PCS to the ParamILS standard, your floating point ranges are discretized with a granularity stepsize of 20, taking into account whether your parameter is linear or log.
```

### PCS

The PCS format is the same as SMAC2. However, as ParamILS does not support continuous ranges, Sparkle converts the parameters to a set with granularity of 20.

**References**

<a id="1">[1]</a>
Sequential Model-Based Optimization for General Algorithm Configuration
F. Hutter and H. H. Hoos and K. Leyton-Brown (2011)
Proc.~of LION-5, 2011, p507--523

<a id="2">[2]</a>
SMAC3: A Versatile Bayesian Optimization Package for Hyperparameter Optimization
Marius Lindauer and Katharina Eggensperger and Matthias Feurer and André Biedenkapp and Difan Deng and Carolin Benjamins and Tim Ruhkopf and René Sass and Frank Hutter (2022)
Journal of Machine Learning Research, 2022, p1--9

<a id="3">[3]</a>
The irace package: Iterated Racing for Automatic Algorithm Configuration,
Manuel López-Ibáñez and Jérémie Dubois-Lacoste and Leslie Pérez Cáceres and Thomas Stützle and Mauro Birattari (2016)
Operations Research Perspectives, Volume 3, p43--58

<a id="4">[4]</a>
ParamILS: An Automatic Algorithm Configuration Framework
Frank Hutter, Holger H. Hoos, Kevin Leyton-Brown, and Thomas Stützle. (2009)
Journal of Artificial Research 2009, volume 36, pages 267-306.
