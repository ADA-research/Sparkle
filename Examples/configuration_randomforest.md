### Configuring Random Forest on Iris

We can also use Sparkle for Machine Learning approaches, such as Random Forest for the Iris data set. Note that in this case, the entire data set is considered as being one instance.

#### Initialise the Sparkle platform

```bash
sparkle initialise
```

#### Add instances

```bash
sparkle add_instances Examples/Resources/Instances/Iris
```

#### Add solver

```bash
sparkle add_solver Examples/Resources/Solvers/RandomForest
```

#### Configure the solver on the data set

```bash
sparkle configure_solver --solver RandomForest --instance-set-train Iris --objectives accuracy:max

sparkle wait
```

Validate the performance of the best found parameter configuration. The test set is optional.

```bash
sparkle validate_configured_vs_default --solver RandomForest --instance-set-train Iris --objectives accuracy:max
```

#### Generate a report

Wait for validation to be completed

```bash
sparkle wait
```

Generate a report detailing the results on the training (and optionally testing) set.

```bash
sparkle generate_report --objectives accuracy:max
```