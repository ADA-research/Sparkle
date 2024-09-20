# Contributing

For now, the development of Sparkle is done by a closed core team.

We will gladly accept contributions in the form of bug reports, feature requests and pull requests in the near future, when the appropriate infrastructure is in place, and the code base is ready.

## Issue creation protocol
When finding a bug or an issue in Sparkle, feel free to create an issue in [Jira](https://kvdblom.atlassian.net/jira/software/c/projects/SPRK/boards/1) if you are part of the closed core team.
Check before you create a new issue if there already exists one that addresses the bug you found.
In case an existing issue already partially covers the bug, you could add a comment to that issue, to ensure your bug is covered by it.
Otherwise, you should create a new issue.

### Issue contents checklist
- **Summary**
  - Give a one sentence summary of what the bug or issue is about.
  - Estimate how much work you think addressing the issue takes ranging from XS, S, M, L, to XL and put this between brackets at the beginning of the summary.
  - For bugs, clearly indicate whether it affects the `main` branch to facilitate a fix being expedited and quickly merged into the `main` branch.
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
  - Assign bugs as high priority and improvements as medium.
- **Assign**
  - If the issue is related and isolated to the part of Sparkle you are working on, feel free to assign the issue to yourself. Otherwise, leave it unassigned.

## Branching for issues and bugs
In general, give branches a descriptive name (e.g., by creating the branch through the related Jira issue, which uses the issue ID and name in the branch name).

### Bugs affecting the `main` branch
For bug fixes affecting the `main` branch, create a branch from `main`, and implement the fix there. If unsure, first try to reproduce the bug on the `main` branch.
When ready, create a pull request towards the `main` branch, clearly indicating it should also be merged into the `development` branch.
Make sure to also update the `CHANGELOG.md` and the version number with a minor version (after the dot) when ready to merge to main. E.g., 0.4.1 changes to 0.4.2.

### All other development
The development is done on the `development` branch. Before starting your own work, make sure you have the pre-commit pipeline installed to avoid any flake8 issues on the GitHub, by running `pre-commit install` in the sparkle environment.
To make changes to Sparkle, please create a branch from `development` and add your code there.
If, during testing, you need to clean up local files, please do so using the custom git command `git sparkle-clean` as this preserves certain untracked files that are necessary to run Sparkle (and which would be removed when simply running `git clean -dxf`). To make this command locally available, run `git config alias.sparkle-clean "clean -dxf -e SparkleAI.egg-info"` once.
When ready, create a pull request towards the `development` branch.

## Pull requests, review, and merge protocol
1. Prior to creating a pull request, **the author(s) of the changes are expected to ensure the general, code style and testing conditions below are satisfied**. To avoid burning through our build minutes on Github, this is easily tested locally by running "flake8" or "pytest" in the main sparkle directory in your branch.
2. Pull requests should be reviewed by at least one member of the Sparkle development team.
3. Once all reviewers have approved the pull request it can be merged. Make sure issue branches are deleted upon merger to avoid excessively many dormant branches. In principle the last reviewer to approve should do the merge immediately. However, if this does not work because, e.g., a final (minor) change is requested, or they forget, someone else can take over the responsibility.

### General
1. Ensure the branch to be merged is up-to-date with the target branch.
2. Ensure the pipelines run successfully within the `sparkle` conda environment.
3. Ensure a useful and accurate entry to the `CHANGELOG.md` is included.
4. Ensure tests are adapted or new ones are created to cover possible new functionalities.
5. In case of changes to the `environment.yml` or `dev-env.yml` make sure it installs correctly. Since the environment can affect all code, make sure ALL tests, examples, etc. run correctly.
6. Carefully check any changes to files in the `Settings/` directory. Are they truly needed?

### Code style
The coding style consistency is a work in progress, and existing code may not adhere to the points below. Please favour the style discussed here over the style of whatever existing code you are working on, so we can gradually move to a consistent code base.

1. Ensure the code is easily readable and understandable.
2. Ensure comments explain code that cannot be written in an easily readable and understandable way.
3. Adhere to the [PEP8](https://pep8.org/) style guide. Deviations are documented in `.flake8` (only larger line length).
3. Make sure the code style rules pass by running `flake8`.
4. Ensure useful and accurate docstrings are included, and follow the [Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) for them. End parameter description sentences always with a dot.
5. Ensure useful and accurate type hints are included.
6. Use fstrings over other string formatting.
7. Use pathlib over other path manipulators.
8. Prefer interpretable function names over shorter ones.

### Testing
1. Make sure the unit tests pass by running `pytest`.
2. Make sure the integration tests (see `tests/CLI/`) relevant for the commands affected by the changes pass by running them. Optionally run all of them with `tests/CLI/all.sh`.
3. Make sure the examples relevant to the changes execute correctly (see the `.sh` files in `Examples/`).

## Release protocol
When releasing a new version (including bugfix versions) of Sparkle to the `main` branch, the protocol below should be followed. First the checks should be performed. If at any step anything fails, it should first be fixed and then ALL checks should be performed again from scratch, starting from point 1.

### Checks
1. Freshly install the conda environment. Remove the old one with `conda env remove -n sparkle` and create it again with `conda env create -f environment.yml` or with `conda env create -f dev-env.yml`. In principle, these environments are equal except that the dev-env has a few extra libs to run pytests and flake8.
2. Make sure the code style rules pass by running `flake8` (make sure the `sparkle` conda environment is installed and active).
3. Make sure the unit tests pass by running `pytest` (make sure the `sparkle` conda environment is installed and active).
4. Make sure the integration tests pass by running `tests/CLI/all.sh` (make sure the `sparkle` conda environment is installed and active).
5. Make sure the examples in `Examples/` execute correctly (all `.sh` files).
6. Only if all checks were passed successfully, move on to the steps for release. Otherwise, first fix what is failing and then re-do all the checks.

### Release
1. Create a branch with the version number of the release from the `development` branch, named ``release/$VERSION''
2. Update and commit `CHANGELOG.md` by creating a header with the release number and date; move everything from the `[unreleased]` header to the new release header (leaving the `[unreleased]` header empty for the next release).
3. Update and commit `sparkle/about.py` by changing the version number.
4. If there were updates to the CLI and/or the examples.md, make sure to re-compile their files for the Documentation. Run `md_to_sh.py` in the Documentation directory to compile the example .mds to executable .sh files, and run `command_descriptions.py` to automatically re-create the documentation for the CLI commands and their arguments. Run `mod_descriptions.py` to update the package descriptions. The documentation itself is after release automatically compiled and deployed to github pages.
4. Create the compiled zip for PyPi by running `python setup.py sdist bdist_wheel`. Delete build directory and the wheel file, and commit it.
5. Merge the new version branch into both `development` and `main`, DO NOT delete the version branch!
6. Upload the zip to PyPi with `twine upload $ZIPFILE_PATH`

## CHANGELOG

The file `CHANGELOG.md` aims to track changes between versions.
When making changes, please add a short description in the `[Unreleased]` section, under a relevant subsection (`Added`, `Changed`, `Fixed`, `Removed` or `Deprecated`).

## Tests
Sparkle has a variety of tests to make sure our changes impact the code base in the intended manner of the developer.

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
These tests are in `tests/CLI/*`. In general these have been designed to run on a Slurm cluster, however some have been made available to run locally on Linux/MacOS. It is imperative that it functions on Slurm, and ideally has the same behaviour locally/without Slurm.

