### Example usage of Sparkle for parallel algorithm portfolio
### The example illustrates the use of an decision algorithm that uses runtime as measurement

## Initialise the Sparkle platform

`Commands/initialise.py`

## Add instances 
Add instances (in this case for the portfolio) in a given directory, without running solvers or feature extractors
Note that you should use the full path to the folder containing the instance(s)

`Commands/add_instances.py --run-solver-later --run-extractor-later Examples/Resources/Instances/PTN/`

## Add solvers

Add a solver with a wrapper containing the executable name of the solver and a string of command line parameters, without running the solver yet
The path used should be the full path to the solver directory and should contain the solver executable and the `sparkle_smac_wrapper.py` wrapper

If needed solvers can also include additional files or scripts in their directory, but try to keep additional files to a minimum as it speeds up copying.
Use the --solver-variations option to set the default number of solver variations of a solver which will be used when a portfolio is constructed.

`Commands/add_solver.py --run-solver-later --deterministic 0 Examples/Resources/Solvers/CSCCSat/`

`Commands/add_solver.py --run-solver-later --deterministic 0 Examples/Resources/Solvers/MiniSAT/`

`Commands/add_solver.py --run-solver-later --deterministic 0 Examples/Resources/Solvers/PbO-CCSAT-Generic/`

## Construct the portfolio

The construction of the portfolio uses all the added solvers in the Solver/ directory and keeps in mind the default overwrite setting
Overwrite is only used if a portfolio is constructed holding the same name as an already existing portfolio.
This will happen by default unless the nickname option is used then this will throw an error

The --nickname option can be used to name your portfolio, the option must be followed by a nickname to name your portfolio. 
For example '--nickname runtime_experiment', if this option is not used then the default nickname is used
This is sparkle_parallel_portfolio
Without using the --solver option all solvers will be added, if you want, for example, only a subset of solvers from the Solver/ directory 
you can use a space seperated list, like --solver Solvers/CSCCSat Solvers/PbO-CCSAT-Generic or --solver Solvers/TCA Solvers/MiniSAT

In order to add multiple variations of a single solver you have to add ',number_of_solver_variations' within the space seperated solver list.
For example --solver Solvers/PbO-CCSAT-Generic,4 which will create a portfolio containing four variations of PbO-CCSAT-Generic

`Commands/construct_sparkle_parallel_portfolio.py --nickname runtime_experiment`

## Run the portfolio 

By running the portfolio a list of jobs will be created which will be executed by the cluster.
Use the --cutoff-time to specify the allotted time of which the portfolio is allowed to run.
add --portfolio-name to specify a portfolio otherwise it will select the latest constructed portfolio

The --instance-paths option must be followed by a space seperated list of paths to an instance or an instance set.
For example --instance-paths Instances/Instance_Set_Name/Single_Instance Instances/Other_Instance_Set_Name

`Commands/run_sparkle_parallel_portfolio.py --instance-paths Instances/PTN/ --portfolio-name runtime_experiment`

## Generate the report

The report details the experimental procedure and performance information. 
This will be located at Components/Sparkle-latex-generator-for-parallel-portfolio/Sparkle_Report.pdf

`Commands/generate_report.py`
