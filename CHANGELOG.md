# Changelog for Sparkle

Notable changes to Sparkle will be documented in this file.

## [0.7] - 2024/04/05

### Added
- SMAC target algorithm, a SMAC handler that takes in input from SMAC and structures it for the targeted solvers. Takes solver output and yields it to SMAC. Preparation for detaching from SMAC to allow for various optimizers in Sparkle.

### Changed
- All SBATCH scripts in sparkle are no longer internally generated but are now done by a sub-library called RunRunner
- Smac dir is automatically cleaned after use of unnecessary files to reduce bloating
- Forked AutoFolio repository
- Configuration scenarios keeps track of its own settings, not general Settings class
- Changed environment .ymls for Pandas requirements
- Started to add in Multi-Objective support. Currently users can specify MO, but SMAC can not handle this for configuration. When this happens, users are warned that the first objective is selected.
- (!) Major code refactorings and redudant code removal

### Fixed
- Fixed AutoFolio parameter warnings
- Fixed various risks with executing subscripts with os.system, now uisng subprocess everywhere instead
- User inputted sbatch options (slurm settings) are always superior and will overwrite any presets
- Got rid of unnecesarry delays around executing runrunner across various nodes
- Fixed AutoFolio compatibility with SMAC 1.4

## [0.6] - 2023/12/14

### Added
- Added support for several commands to run without Slurm, accessible through new --run-on local argument
- Added configurable aggregation function for Marginal Contribution
- Added documentation for running configured solver
- Added type hints

### Changed
- Marginal Contribution of a solver is now implemented according to mathematical definition

### Fixed
- Minor bug fixes and more unit test support added to avoid bugs

## [0.5] - 2023/03/16

### Added
- Instructions in `CONTRIBUTING.md` on how to deal with branching and merging for bug fixes.

### Changed
- Changed several hard coded Slurm settings to now be based on the settings file or user input.
- Include linting for fstrings with `flake8-use-fstring` and make the code comply.
- Include linting for security issues with `flake8-bandit` and make the code comply.
- Changed author list in `README.md` to updated list of maintainers and contributors.
- Update contact email in `README.md`.
- The `sparkle_wait.py` command now fails nicely with an error message when called before any jobs exist to wait for (instead of a hard crash).

### Fixed
- Fixed calls to Slurm's `squeue` command to request an exact output format to ensure robustness against different Slurm configurations.
- Fixed an issue where newer versions of Slurm (>= 22.05.0) occasionally cause problems when launching scripts from an interactive job (<https://bugs.schedmd.com/show_bug.cgi?id=14298>).
- Fix issue with retrieving instance set names for configuration with instance features.

## [0.4] - 2023/01/16
### Added
- New option --run-on in run\_solvers.py 
- Integration with runrunner to run the solvers and related code on the local machine
- Experimental implementation for integration with runrunner to run the solvers on a Slurm clusters. Old style Slurm use is still the default, but optionally Slurm can be used through runrunner with --run-on=slurm\_rr
- Add issue creation, pull request, reviewing, and merging guidelines to `CONTRIBUTING.md`

### Changed
- Include linting for docstrings with `flake8-docstrings` and make the code comply.
- Switch from single quote use to double quote use.

### Fixed
- Fix an issue with the default partition in the Slurm settings causing execution with Slurm to fail on systems where this partition does not exist.

### Removed
- Removed dead code.

## [0.3] - 2022/09/05
### Added
- New option --run-solver-now in add\_solver.py and add\_instances.py
- New option --run-extractor-now in add\_instances.py and add\_feature\_extractor.py
- New command run\_configured\_solver.py to run the last configured solver with its configured parameters on new instances
- Parallel algorithm portfolios with the commands construct\_sparkle\_parallel\_portfolio.py and run\_sparkle\_parallel\_portfolio.py

### Changed
- Default to --run-solver-later in add\_solver.py and add\_instances.py
- Default to --run-extractor-later in add\_instances.py and add\_feature\_extractor.py
- Updated documentation, examples and tests for new behaviour of --run-solver-later and --run-extrator-later
- Improve integration tests so all launched jobs are cancelled upon test completion
- Change the list of authors in about.py to be in alphabetical order
- Update runsolver version to 3.4

### Fixed
- Removed the unneeded globals in sparkle\_global\_help.py
- Changed solver and instance paths in Examples/configuration_quality.sh and Examples/configuration_quality.md
- Updated generate_report_for_configuration.sh test to new internal configuration scenario directory naming convention

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
- Separate configuration for different train and test sets
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

### Changed

### Fixed

### Removed

## [Known issues]
- On some Slurm configurations problems may arise when running scripts. This is linked to the environment in which the script is running. We are investigating solutions to this issue.
