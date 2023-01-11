# Contributing

For now, the development of Sparkle is done by a closed core team.

We will gladly accept contributions in the form of bug reports, feature requests and pull requests in the near future, when the appropriate infrastructure is in place, and the code base is ready.

The development is done on the `development` branch. 
To make changes to Sparkle, please create a branch from `development`, give it a descriptive name and add your code there.
When ready, create a pull request towards the `development` branch.

## Issue creation protocol
When finding a bug or an issue in Sparkle, feel free to make an issue for it. 
Check before you create a new issue if there already exists one that addresses the bug you found.
In case an existing issue already partially covers the bug, you could add a comment to that issue, to ensure your bug is covered by it.
Otherwise, you should create an issue. 

### Issue contents checklist
- **Summary**
  - Give a one sentence summary of what the bug or issue is about.
  - Estimate how much work you think addressing the issue takes ranging from XS, S, M, L, to XL and put this between brackets at the beginning of the summary.
- **Contents**
  - Describe the problem in more detail.
    - Attach files or output logs when appropriate.
  - Give instructions on how to reproduce the error.
    - This could be commands to run.
  - Make a suggestion on how to fix the issue if you have one.
- **Type**
  - Most issues will either be a `bug` or a `task`. A bug should fix an error, whereas a task should be an improvement.
  - `epic` and `story` are reserved for overarching issue management and should only be used in agreement with lead developers. 
- **Priority**
  - Assign bugs as high priority and improvements as medium improvements for now.
- **Assign**
  - If the issue is related and isolated to the part of Sparkle you are working on, feel free to assign the issue to yourself. Otherwise, leave it unassigned.

## Pull requests, review, and merge protocol
1. Before a pull request is reviewed, the author(s) of the changes are expected to ensure the general, code style and testing conditions below are satisfied.
2. Pull requests should be reviewed by at least one member of the Sparkle development team.
3. Once all reviewers have approved the pull request it can be merged. Make sure issue branches are deleted upon merger to avoid excessively many dormant branches. In principle the last reviewer to approve should do the merge immediately. However, if this does not work because, e.g., a final (minor) change is requested, or they forget, someone else can take over the responsibility.

### General
1. Ensure the branch to be merged is up-to-date with the target branch.
2. Ensure the pipelines run successfully within the `sparkle` conda environment.
3. Ensure a useful and accurate entry to the `CHANGELOG.md` is included.
4. Ensure tests are adapted or new ones are created to cover possible new functionalities.
5. In case of changes to the `environment.yml` make sure it installs correctly. Since the environment can affect all code, make sure ALL tests, examples, etc. run correctly.
6. Carefully check any changes to files in the `Settings/` directory. Are they truly needed?

### Code style
The coding style consistency is a work in progress, and existing code may not adhere to the points below. Please favour the style discussed here over the style of whatever existing code you are working on, so we can gradually move to a consistent code base.
1. Ensure the code is easily readable and understandable.
2. Ensure comments explain code that cannot be written in an easily readable and understandable way.
3. Adhere to the [PEP8](https://pep8.org/) style guide. Deviations are documented in `.flake8` (only larger line length).
3. Make sure the code style rules pass by running `flake8`.
4. Ensure useful and accurate docstrings are included, and follow the [Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) for them.
5. Ensure useful and accurate type hints are included.
6. Use fstrings over other string formatting.
7. Use pathlib over other path manipulators.
8. Prefer interpretable function names over shorter ones.

### Testing
1. Make sure the unit tests pass by running `pytest`.
2. Make sure the integration tests (see `Commands/test/`) relevant for the commands affected by the changes pass by running them. Optionally run all of them with `Commands/test/all.sh`.
3. Make sure the examples relevant to the changes execute correctly (see the `.sh` files in `Examples/`).

## Release protocol
When releasing a new version of Sparkle to the main branch, the protocol below should be followed. First the checks should be performed. If at any step anything fails, it should first be fixed and then ALL checks should be performed again from scratch, starting from point 1.

### Checks
1. Freshly install the conda environment. Remove the old one with `conda env remove -n sparkle` and create it again with `conda env create -f environment.yml`
2. Make sure the code style rules pass by running `flake8` (make sure the `sparkle` conda environment is installed and active).
3. Make sure the unit tests pass by running `pytest` (make sure the `sparkle` conda environment is installed and active).
4. Make sure the integration tests pass by running `Commands/test/all.sh` (make sure the `sparkle` conda environment is installed and active).
5. Make sure the examples in `Examples/` execute correctly (all `.sh` files).
6. Only if all checks were passed successfully, move on to the steps for release. Otherwise, first fix what is failing and then re-do all the checks.

### Release
1. Create a branch with the version number of the release from the development branch
2. Update and commit `CHANGELOG.md` by creating a header with the release number and date; move everything from the `[unreleased]` header to the new release header (leaving the `[unreleased]` header empty for the next release).
3. Merge the new version branch into both development and main, DO NOT delete the version branch!

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

