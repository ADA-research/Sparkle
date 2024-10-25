# Configurators

Sparkle offers several configurators to use for Algorithm Configuration. Although they come with automatic installations and various default settings, you might need to set up a few details for your specific system and algorithm or data set to make sure everything works as intended.

## SMAC2

Sequantial Model-Based Optimization for General Algorithm Configuration[[1]](#1), or [SMAC]((https://www.cs.ubc.ca/labs/algorithms/Projects/SMAC)) for short is a Java based algorithm configurator. *Note that this the second version, and not SMAC3 the Python version*. The original documentation of the configurator can be found [here](https://www.cs.ubc.ca/labs/algorithms/Projects/SMAC/v2.10.03/manual.pdf).

```{note}
SMAC2 is written in Java and therefore requires Java to be installed in your environment. The current tested version in Sparkle is 1.8.0_402
```

## IRACE

Iterated Racing for Automatic Algorithm Configuration[[2]](#2), or [IRACE](https://mlopez-ibanez.github.io/irace/) for short is an R based algorithm configurator. The full documentation of the configurator can be found [here](https://cran.r-project.org/web/packages/irace/vignettes/irace-package.pdf).

IRACE offers many parameters that can be set, but also automatically computed in accordance with their paper[[2]](#2) and we recommend not deviating from those formulae as it may result in unexpected behaviour.

```Note
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

The MaxTime parameter specifies the budget in terms of maximum runtime of the target algorithm (e.g. your Solver in the Sparkle Platform). Sparkle measures the time spend of your solver using RunSolver, and passes the **CPU** time to IRACE to determine its spend budget. IRACE also tries to determine how much budget it has for the first run using the `budgetEstimation` parameter, which is by default set to 2%. Sparkle will attempt to recompute this based on `target_cutoff_time` (The time limit of your Solver in each call) and the `max_time` budget as $\frac{target_cutoff_time}{max_time}$, but only if the fraction is less than 1.0.

## References

<a id="1">[1]</a>
Sequential Model-Based Optimization for General Algorithm Configuration
F. Hutter and H. H. Hoos and K. Leyton-Brown (2011)
Proc.~of LION-5, 2011, p507--523

<a id="2">[2]</a>
The irace package: Iterated Racing for Automatic Algorithm Configuration,
Manuel López-Ibáñez and Jérémie Dubois-Lacoste and Leslie Pérez Cáceres and Thomas Stützle and Mauro Birattari (2016)
Operations Research Perspectives, Volume 3, p43--58
