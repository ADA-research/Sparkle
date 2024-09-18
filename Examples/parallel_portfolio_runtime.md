## Running a Parallel Portfolio
In this tutorial we will measure the runtime performance of several algorithms in parallel. The general idea is that we consider the algorithms as a portfolio that we run in parallel (hence the name) and terminate all running algorithms once a solution is found.

### Initialise the Sparkle platform

```bash
sparkle initialise
```

### Add instances
First we add the instances to the platform that we want to use for our experiment. Note that if our instance set contains multiple instances, the portfolio will attempt to run them all in parallel.
Note that you should use the full path to the directory containing the instance(s)

```bash
sparkle add_instances Examples/Resources/Instances/PTN/
```

### Add solvers
Now we can add our solvers to the portfolio that we want to "race" in parallel against eachother.
The path used should be the full path to the solver directory and should contain the solver executable and the `sparkle_solver_wrapper` wrapper. It is always a good idea to keep the amount of files in your solver directory to a minimum.

```bash
sparkle add_solver Examples/Resources/Solvers/CSCCSat/
sparkle add_solver Examples/Resources/Solvers/MiniSAT/
sparkle add_solver Examples/Resources/Solvers/PbO-CCSAT-Generic/
```

### Run the portfolio 

By running the portfolio a list of jobs will be created which will be executed by the cluster.
Use the `--cutoff-time` option to specify the maximal time for which the portfolio is allowed to run.
add `--portfolio-name` to specify a portfolio otherwise it will select the last constructed portfolio

The `--instance-path` option must be a path to a single instance file or an instance set directory.
For example `--instance-path Instances/Instance_Set_Name/Single_Instance`.

If your solvers are non-deterministic (e.g. the random seed used to start your algorithm can have an impact on the runtime), you can set the amount of jobs that should start with a random seed per algorithm. Note that scaling up this variable has a significant impact on how many jobs will be run (Number of instances * number of solvers * number of seeds). We can set using the `--solver-seeds` argument followed by some positive integer.

```bash
sparkle run_parallel_portfolio --instance-path Instances/PTN/ --portfolio-name runtime_experiment
```

### Generate the report

The report details the experimental procedure and performance information. 
This will be located at `Output/Parallel_Portfolio/Sparkle_Report.pdf`

```bash
sparkle generate_report
```
