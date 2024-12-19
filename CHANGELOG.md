# Changelog for Sparkle

Notable changes to Sparkle will be documented in this file.

## [0.9.2] - ??

### Fixed
- Bugs regarding using Configuration with instance features [SPRK-364]
- Allow user to easily recompile runsolver with initialise command for Venv support [SPRK-367]
- Added performance data argument to clean up command [SPRK-367]
- Updated wait command to yield more information when jobs are finished [SPRK-367]

### Added
- Added documentation on how to use Venv instead of Conda for Sparkle [SPRK-367]
- Added autocompletion for Sparkle CLI [SPRK-332]

## [0.9.1.2] - 2025/12/12

Patchfix

### Fixed
- Execution rights on internal package CLI files were removed during pip installation
- Various bugfixes regarding nicknames

### Changed
- run_configured_solver command has now been merged into run_solvers [SPRK-361]

## [0.9.1] - 2024/12/08

### Added
- Added the SMAC3 configurator to Sparkle [SPRK-335]
- Added no-copy argument to all CLI add commands so the user can create symbolic links to their files instead of copying [SPRK-356]
- Added no-save argument to initialise command [SPRK-358]
- Added SolutionFileVerifier to verify instance solutions from CSV file [SPRK-360]

### Changed

- Generate report command (Configuration report) now checks whether there are still jobs that should be run before allowing the user to start this command [SPRK-328]
- PerformanceDataFrame now directly subclasses from Pandas DataFrame instead of functioning as a container class [SPRK-278]
- Initialise command no longer removes the user's Settings directory if a platform already exists, but does still save it to the snapshot. [SPRK-355]
- Solver configuration now stores found configurations and their results in the PerformanceDataFrame [SPRK-358]
- run_solvers_core is integrated now into the solver class [SPRK-358]
- configure solver command now also runs default configuration, schedules train set validation and test set validation if given [SPRK-358]
- Modified SolutionVerifier adding to solvers as a CLI argument that is saved in the Solver meta file instead of in the Settings file [SPRK-359]
- PAR objective now takes into account 'negative status' and penalises solvers for crashing or incorrect answers [SPRK-360]

### Removed
- Validate configured vs default command has been removed as it is now redundant [SPRK-358]
- Validator class has been removed as it is no longer relevant [SPRK-358]

## [0.9.0] - 2024/10/30

### Added
- Added cancel command to Sparkle to cancel Slurm jobs including interactive table to make your selection [SPRK-338]
- Added the IRACE configurator to Sparkle, which works 'out of the box' with the Conda Environment (Only R is user supplied) [SPRK-290]

### Changed
- RunSolver logging paths are now passed as a parameter instead of placed in CWD [SPRK-344]
- Most commands are no longer using a specific WD and instead are executed from the platform dir
- ConfigurationScenarios can now be re-created from file and be detected based on Configurator/Solver/Instance set combination [SPRK-201]
- Updated various package dependencies to their latest versions

### Fixed
- Reporting changes when default settings were used [SPRK-319]
- Bug when generating configuration report for quality [SPRK-298]

## [0.8.9] - 2024/09/27
- Various updates to Documentation, automated testing and CI pipelines

### Fixed
- Bugfix for generating figures in report generation for 'configuration_quality' tutorial

## [0.8.8] - 2024/09/20

### Changed
- ConfiguratorScenario is now a template class that must be implemented by each configurator
- Documentation has been completely revamped

## [0.8.6] - 2024/09/16

### Changed
- SparkleObjectives are now used platform wide to define what metrics should be collected from Solvers and stored, how they should be treated (Minisation, aggregation), and can be easily set by the user. They can be overriden with custom implementations by the user.

## [0.8.5] - 2024/09/02

### Changed
- Solver wrappers have been simplified in their usage and extra tools are available to the user [SPRK-274]
- Solver dict parsing hase been simplified [SPRK-310]
- InstanceSet object has been expanded to now support ML task based data sets [SPRK-325]
- RunRunner logging is now forwarded to CLI call log, all RunRunner generated files and logs are placed in the same dir instead of Tmp [SPRK-330]
- PCSParser has been added to the Sparkle Tools instead of installed from Github [SPRK-334]

### Added
- Generating a report now includes a JSON serialised version of all the output data [SPRK-79]

### Fixed
- Many methods/properties used string variables where Path was needed and have been changed accordingly [SPRK-222]


## [0.8.4] - 2024/07/30

### Changed
- Sparkle's CLI and file I/O file structure is now completely directory independent, allowing users to initialise a platform in any directory and run the commands. This also allows Sparkle to be pip installed completely independently, except for the Conda environment creation.
- Sparkle commands now support spaces instead of underscores to, allowing users to run ``sparkle add instances`` instead of ``sparkle add_instances``, for a more natural way of typing.

### Added
- Examples can be downloaded when initialising sparkle with the ``--download-examples`` argument for the ``sparkle initialise`` command.

## [0.8.3] - 2024/07/24

### Changed
- The use of --parallel arguments is now deprecrated and all related functionality is now controlled by the settings file general number of jobs parallel setting. [SPRK-275]
- The slurm_settings are now handled by the general sparkle settings, where the user can add any unknown options to the Slurm settings
- Components are now part of the sparkle library directory, to ensure existence after pip install.
- The wait command has had a major revision, now aimed to encapsulate all information presented by squeue. Can be turned off to work as in previous version by turning verbosity to quiet in settings.
- Extractors now have a preliminary object representation.
- SparkleFeatureDataCSV has been replaced with FeatureDataFrame.
- FeatureDataFrame and PerformanceDataFrame are now sorted after initialisation (once) to avoid slow look up by pandas.DataFrame.loc.
- Marginal Contribution computation (Virtual Best) now mostly done by PerformanceDataFrame. Cap values no longer part of computation and most be done beforehand.
- Ablation scenarios are now stored in the Output/Ablation directory, and the validation is stored in a subdirectory of the scenario.
- Feature extractors can now define feature groups and can be parallelised per feature group.
- Solver return status are now defined as an Enum instead of strings.

### Added
- Object representation for Instance Sets. Can deal with Multi-file instances, and single instances are considered a set of one.
- Documentation website has a new design and GitHub pages has been added instead of Read the Docs, and will soon replace Read the Docs. Can already be seen on Github pages.
- The run-on argument is now also available as a general setting, which will be overriden if the CLI argument is also given.
- SATZilla2024 has been added to the Example feature extractors.

### Fixed
- Bug fix regarding the retrieval of the best configuration from SMAC2.
- When changing settings in between commands, Sparkle no longer crashes when a whole section has been removed.
- Bug fix regarding running AutoFolio selector on a single instance after training.
- Bug fix for ablation analysis missing parameters, now they will be supplemented with the default values from PCS file.

### Removed
- Command run_status has been removed as a Command, as it is no longer yields more information than the Wait command

## [0.8.2] - 2024/06/19

### Changed
- Nickname system has been re-evaluated and is now available in any command. CLI now supports nickname, directory name and path as inputs for Instances/Solvers/Extractors. [SPRK-55]
- The Sparkle environment has swig updated to 4.0.2 [SPRK-187] and Runsolver to 219 [SPRK-219].
- CLI arguments are now unified into one file for user readiblity and to reduce maintenance cost. [SPRK-265]

### Added
- Runsolver is now automatically compiled upon running CLI initialisation if the executable does not exist. [SPRK-75]
- Sparkle settings now support multiple budget types for configurators: Number of solver calls, Wall-clock, CPU-time. [SPRK-76]
- PCS files for configuration are checked if they can be parsed. [SPRK-80]
- Status command now also checks configurator logs for errors [SPRK-82] 
- The user is now notified by the CLI when changing settings values in between commands. [SPRK-88]
- Added a template for feature extractors. [SPRK-102]
- The user is notified if the submitted solver does not have correct executable rights for the CLI. [SPRK-120]
- The Sparkle setting clis_per_node is now renamed to max_parallel_runs_per_node, but the old name is still supported. [SPRK-128]
- Sparkle now uses its own validation implementation instead of the one given by SMACv2, allowing validation to run in parallel instead of sequential. [SPRK-270]

### Fixed
- AutoFolio cutoff time was set to an odd value. Now matches the original paper. [SPRK-220]
- The parallel portfolio runner has had a complete rework, resulting in the disabling of support for the QUALITY objective.[SPRK-269]
- Bug in removing a solver in the CLI, resulting in it still being present in some parts. [SPRK-276]
- Bug fix for AutoFolio when running portfolio for selection. [SPRK-281]


## [0.8] - 2024/04/29

### Added
- Awaiting Sparkle Jobs is now done using RunRunner's objects and .JSON files instead of direct calls to Slurm
- Performance data now is restructured into Performance DataFrame which supports two new dimensions: Objective and Run.
- Sparkle commands are now registered directly as command line operators by prefix ``sparkle'', see updated examples.

### Changed
- ! New file structure for code was implemented, Commands are now in CLI folder and library objects and methods are in sparkle directory.
- Runsolver is now automatically provided for newly added Solvers to the Sparkle Platform
- Output directories for report generation are now compliant with the explanation in the documentation
- Configurator object is now used as source in many cases when accessing Configurator directories instead of hard-coded
- Refactored many redundant methods out of the codebase
- Removed development environment and merged into sparkle environment
- Moved package to Github instead of Bitbucket

### Fixed
- latest_scenario now uses a getter
- QUALITY was removed from PerformanceMeasure enum
- Reports now use one bibliograpghy file instead of multiple
- Java SMAC is no longer called through each_smac_run_core but adressed directly by Sparkle
- Fixed bugs for running configured solver

## [Known issues]
- Running configured solver in parallel now tends to lead to empty raw output files from the solver. This will be either solved in the next version.

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
- The `wait.py` command now fails nicely with an error message when called before any jobs exist to wait for (instead of a hard crash).

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
- Converted `CLI/*.py` to the new coding style
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
