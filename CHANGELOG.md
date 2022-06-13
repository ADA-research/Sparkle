# Changelog for Sparkle

Notable changes to Sparkle will be documented in this file.

## [0.2] - 2021/09/08
### Added
- Automatic testing system based on pytest (in `./tests`)
- Add a coding style (in `.flake8` file)
- Activated CI/CD for testing and coding style
- New installation process using an conda environment
- Created two separated environments (conda) for users or devs 
- Published the documentation on https://sparkle-ai.readthedocs.io/
- Created a `CHANGELOG.md` file documenting the changes to Sparkle
- Created a `CONTRIBUTING.md` file explaining how to contribute
- Set the licence to an MIT licence
- Added `epstopdf.pl` to the distribution to ease install
- Added the test instance name to the output and validation dirs
- Extended check for ablation
- Add VRP\_SISRs src dir to gitignore
- Add VRP\_SISRs source, update related things, and move to CVRP directory
- Update MinVC instance description
- Add source code and installation instructions for PbO-CCSAT solver
- Add source code and installation instructions for MiniSAT solver
- Add source code and installation instructions for CSCCSat solver
- Add known descriptions for components, solvers, extractors, and instances
- Update CCAG problem source and descriptions

### Changed 
- Moved the documentation to the Sphinx platform
- Updated the documentation
- Updated the README
- Updated dependencies
- Merge add\_solver\_help.py and add\_configured\_solver\_help.py
- Changed file location of last\_test\_file\_path such that only the solver name is required to find the correct directory
- Seperate configuration for different train and test sets
- Remove ablation scenarios when platform is cleaned
- Change selection report title
- Remove Yahsp solver and Depots instances (unclear redistribution permissions)

### Fixed
- Converted `Commands/*.py` to the new coding style
- Change LaTeX build to non-interactive to prevent hanging
- get\_solver\_directory function and pcs check before configuration
- Make pcs file check only return true iff one pcs file is found
- Remove ablation scenarios when starting a new configuration
- Fix call to unassigned variable
- Hotfix for issue where plotting for configuration reports did not work when zero or negative values existed

## [Unreleased]

### Added
- New option --run-solver-now in add\_solver.py and add\_instances.py
- New option --run-extractor-now in add\_instances.py and add\_feature\_extractor.py
- New command run\_configured\_solver.py to run the last configured solver with its configured parameters on new instances

### Changed
- Default to --run-solver-later in add\_solver.py and add\_instances.py
- Default to --run-extractor-later in add\_instances.py and add\_feature\_extractor.py
- Updated documentation, examples and tests for new behaviour of --run-solver-later and --run-extrator-later
- Improve integration tests so all launched jobs are cancelled upon test completion
- Change the list of authors in about.py to be in alphebetical order
- Update runsolver version to 3.4

### Fixed
- Removed the unneeded globals in sparkle\_global\_help.py 
- Changed solver and instance paths in Examples/configuration_quality.sh and Examples/configuration_quality.md
- Updated generate_report_for_configuration.sh test to new internal configuration scenario directory naming convention

