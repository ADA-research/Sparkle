# Contributing

For now, the development of Sparkle is done by a closed core team.

We will gladly accept contributions in the form of bug reports, feature requests and pull requests in the near future, when the appropriate infrastructure is in place, and the code base is ready.

The development is done on the `development` branch. 
To make changes to Sparkle, please create a branch from `development`, give it a descriptive name and add your code there.
When ready, create a pull request towards the `development` branch.

## Release protocol
When releasing a new version of Sparkle to the main branch, the protocol below should be followed:

1. Freshly install the conda environment. Remove the old one with `conda env remove -n sparkle` and create it again with `conda env create -f environment.yml`
2. Make sure the code style rules pass by running `flake8` (make sure the `sparkle` conda environment is installed and active). If not everything passes, fix it and then start again from point 1. of the release protocol.
3. Make sure the unit tests pass by running `pytest` (make sure the `sparkle` conda environment is installed and active). If not everything passes, fix it and then start again from point 1. of the release protocol.
4. Make sure the integration tests pass by running `Commands/test/all.sh` (make sure the `sparkle` conda environment is installed and active). If not everything passes, fix it and then start again from point 1. of the release protocol.
5. Make sure the examples in `Examples/` execute correctly (all `.sh` files). If not everything passes, fix it and then start again from point 1. of the release protocol.
6. Create a branch with the version number of the release from the development branch
7. Update and commit `CHANGELOG.md` by creating a header with the release number and date; move everything from the `[unreleased]` header to the new release header (leaving the `[unreleased]` header empty for the next release).
8. Merge the new version branch into both development and main, DO NOT delete the version branch!

## CHANGELOG

The file `CHANGELOG.md` aims to track changes between versions. 
When making changes, please add a short description in the `[Unreleased]` section, under a relevant subsection (`Added`, `Changed`, `Fixed`, `Removed` or `Deprecated`).

## Tests

### Unit tests

Sparkle aims to have an extensive test coverage of the functionalities. 
We use the `pytest` platform to automate the testing. 
When writing new code you should create relevant tests in the `tests` directory. 
To see a simple example of the tests, you can check the file `tests/test_about.py`.
You should also read the [pytest documentation](https://docs.pytest.org).

To run the test you can simply run 
```
$ pytest
```
pytest is installed with the base requirements of Sparkle and is run automatically on pull request. 

### Integration tests

In addition to the unit tests, Sparkle also has a series of integration tests verifying that the commands run without errors.
These tests are in `Commands/test/*` and must be run on a Slurm cluster.


## Coding style

Sparkle code follows most of the [pep8](https://pep8.org/) recommendations. 

The differences are:
 * max line length: 89
 * the unused imports are ignored on `__init__.py` files 

To check if your code follows the coding style, you can run
```
flake8
```
flake8 is installed with the base requirements of Sparkle and is run automatically with pull requests. 

