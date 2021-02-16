### Parallel Portfolio example
​
Initialise the Sparkle platform
​
`Commands/initialise.py`
​
Add instances (in CNF format) in a given directory, without running solvers or feature extractors yet
​
`Commands/add_instances.py --run-solver-later --run-extractor-later Examples/Resources/Instances/PTN/`
​
Add solvers with a wrapper containing the executable name of the solver and a string of command line parameters, without running the solvers yet
​
(the directory should contain both the executable and the wrapper)
​
`Commands/add_solver.py --run-solver-later --deterministic 0 Examples/Resources/Solvers/CSCCSat/`
​
`Commands/add_solver.py --run-solver-later --deterministic 0 Examples/Resources/Solvers/Lingeling/`
​
`Commands/add_solver.py --run-solver-later --deterministic 0 Examples/Resources/Solvers/MiniSAT/`
​
Construct a parallel portfolio, using the all solvers and keeping in mind the given settings (default only for now.)
​
`Commands/construct_parallel_portfolio.py`
​
Run the portfolio on the instances; add `--parallel` to run the instances in parallel.
​
`Commands/run_parallel_portfolio.py`
​
Generate an experimental report detailing the experimental procedure and performance information; this will be located at `Components/Sparkle-latex-generator/Sparkle_Report.pdf`
​
`Commands/generate_report.py`
