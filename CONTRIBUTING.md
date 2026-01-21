# Contributing

We gladly accept contributions in the form of bug reports, feature requests and pull requests.

## Issue creation protocol
When finding a bug or an issue in Sparkle, feel free to create an issue on the GitHub.
Check before you create a new issue if there already exists one that addresses the bug you found.
In case an existing issue already partially covers the bug, you could add a comment to that issue, to ensure your bug is covered by it.
Otherwise, you should create a new issue.

### Issue contents checklist
- **Summary**
  - Give a one sentence summary of what the bug or issue is about.
  - For bugs, clearly indicate whether it affects the `main` branch to facilitate a fix being expedited and quickly merged into the `main` branch.
- **Contents**
  - Describe the problem in more detail.
    - Attach files or output logs when appropriate.
  - Give instructions on how to reproduce the error.
    - This could be commands to run.
  - Make a suggestion on how to fix the issue if you have one.
- **Assign**
  - If the issue is related and isolated to the part of Sparkle you are working on, feel free to assign the issue to yourself. Otherwise, leave it unassigned.

## Branching for issues and bugs
In general, give branches a descriptive name (e.g., use the issue ID and name in the branch name).

### All other development
The development is done on the `development` branch. Before starting your own work, make sure you have the pre-commit pipeline installed to avoid any ruff issues on the GitHub, by running `pre-commit install` in the sparkle environment.
To make changes to Sparkle, please create a branch from `development` and add your code there.
When ready, create a pull request towards the `development` branch.

## Pull requests, review, and merge protocol
1. Prior to creating a pull request, **the author(s) of the changes are expected to ensure the general, code style and testing conditions below are satisfied**. To avoid running GitHub actions unnecessarily, run the `pytest` locally before creating a PR or pushing new versions of the PR to GitHub.
2. Pull requests should be reviewed by at least one member of the Sparkle development team.
3. Once all reviewers have approved the pull request it can be merged. Make sure issue branches are deleted upon merger to avoid excessively many dormant branches. In principle the last reviewer to approve should do the merge immediately. However, if this does not work because, e.g., a final (minor) change is requested, or they forget, someone else can take over the responsibility.

### General
1. Ensure the branch to be merged is up-to-date with the target branch.
2. Ensure the pipelines run successfully within the `sparkle` venv.
3. Ensure a useful and accurate entry to the `CHANGELOG.md` is included, which will be flagged by the changelog enforcer otherwise.
4. Ensure tests are adapted or new ones are created to cover possible new functionalities.
5. In case of changes to the dependencies, make sure it installs correctly in a new virtual environment. Since the environment can affect all code, make sure ALL tests, examples, etc. run correctly.

### Code style
The coding style consistency is a work in progress, and existing code may not adhere to the points below. Please favour the style discussed here over the style of whatever existing code you are working on, so we can gradually move to a consistent code base.

1. Ensure the code is easily readable and understandable; use interpetable functions and variable names, preferring longer names over short ones.
2. Ensure comments explain code that cannot be written in an easily readable and understandable way.
3. Adhere to the [PEP8](https://pep8.org/) style guide: Make sure the code style rules pass by running `ruff`.
4. Ensure useful and accurate docstrings are included, and follow the [Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) for them.
5. Ensure useful and accurate type hints are included.

### Testing
1. Make sure the unit tests pass by running `pytest`.
2. Make sure the integration tests (see `tests/CLI/`) relevant for the commands affected by the changes pass by running them. You can execute the integration tests with `pytest --integration`. Optionally run all of the pytests with `pytest --all`.
3. Make sure the examples relevant to the changes execute correctly (see the `.sh` files in `Examples/`).

## Release protocol
When releasing a new version (including bugfix versions) of Sparkle to the `main` branch, the protocol below should be followed. First the checks should be performed. If at any step anything fails, it should first be fixed and then ALL checks should be performed again from scratch, starting from point 1.

### Checks
1. Freshly install the conda environment. Remove the old one with `deactivate` followed by deleting the directory and create it again with `env` followed by `pip install -e .`. Optionally, you can run `pip install -e .[dev]`. In principle, these environments are equal except that the dev environment has a few extra packages to run pytests and ruff.
2. Make sure the code style rules pass by running `ruff` (make sure the `sparkle` conda environment is installed and active).
3. Make sure the unit tests pass by running `pytest` (make sure the `sparkle` conda environment is installed and active). You can combine this step and the next step by running `pytest --all`.
4. Make sure the integration tests pass by running `pytest --integration` (make sure the `sparkle` conda environment is installed and active).
5. Make sure the examples in `Examples/` execute correctly (all `.sh` files).
6. Only if all checks were passed successfully, move on to the steps for release. Otherwise, first fix what is failing and then re-do all the checks.

### Release
1. Update `CHANGELOG.md` by creating a header with the release number and date; move everything from the `[unreleased]` header to the new release header (leaving the `[unreleased]` header empty for the next release). Update `pyproject.toml` by changing the version number. Commit and add a git tag to this commit with the version number as "git commit -m 'VERSION_NUMBER'" followed by "git tag VERSION_NUMBER" and afterwards push.
2. If there were updates to the CLI and/or the examples.md, make sure to re-compile their files for the Documentation. Run `md_to_sh.py` in the Documentation directory to compile the example .mds to executable .sh files, and run `command_descriptions.py` to automatically re-create the documentation for the CLI commands and their arguments. Run `mod_descriptions.py` to update the package descriptions. The documentation itself is after release automatically compiled and deployed to github pages.
3. Merge the `development` branch into `main`, DO NOT delete the development branch!
4. Hit the release button on GitHub.

## CHANGELOG

The file `CHANGELOG.md` aims to track changes between versions. When making changes, please add a short description in the `[Unreleased]` section, under a relevant subsection (`Added`, `Changed`, `Fixed`, `Removed` or `Deprecated`).

## Tests
Sparkle has a variety of tests to make sure our changes impact the code base in the intended manner of the developer.

### Unit tests

Sparkle aims to have an extensive test coverage of the functionalities. We use the `pytest` platform to automate the testing. The unit tests are considered "Golden master tests", as they give a specific input to a unit of code and expect a specific output.

When writing new code you should create relevant tests in the `tests` directory. To see a simple example of the tests, you can check the file `tests/test_about.py`. You should also read the [pytest documentation](https://docs.pytest.org).

To run the test you can simply run
```
$ pytest
```
pytest is installed with the base requirements of Sparkle and is run automatically on pull request.

### End-to-end tests

In addition to the unit tests, Sparkle also has a series of end-to-end smoke tests that verify the commands to run without errors. These tests are in `tests/CLI/*`. In general these have been designed to run on a Slurm cluster, however some have been made available to run locally on Linux. It is imperative that it functions on Slurm, and ideally has the same behaviour locally/without Slurm.

### Performance tests

Sparkle also has high load performance tests that should only be executed locally to verify the impact of running on a cluster on the outcome. Run with `--performance` to inspect, and be prepared to wait several minutes.
