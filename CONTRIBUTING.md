# Contributing

For now, the development of Sparkle is done by a closed core team.

We will gladly accept contributions in the form of bug reports, feature requests and pull requests in the near future, when the appropriate infrastructure is in place and the code base is ready.

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
