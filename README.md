# _Sparkle_

[![tests count](https://ada-research.github.io/Sparkle/_static/junit/junit-badge.svg)](https://ada-research.github.io/Sparkle/_static/junit/index.html)
![tests](https://github.com/ada-research/sparkle/actions/workflows/unittest.yml/badge.svg)
[![coverage](https://ada-research.github.io/Sparkle/_static/coverage/coverage-badge.svg)](https://ada-research.github.io/Sparkle/_static/coverage/index.html)
![linter](https://github.com/ada-research/sparkle/actions/workflows/linter.yml/badge.svg?event=push)
![docs](https://github.com/ada-research/sparkle/actions/workflows/documentation.yml/badge.svg?event=push)

> A Programming by Optimisation (PbO)-based problem-solving platform designed to enable the widespread and effective use of PbO techniques for improving the state-of-the-art in solving a broad range of prominent AI problems, including SAT and AI Planning.

Specifically, Sparkle facilitates the use of:

 * Automated algorithm configuration
 * Automated algorithm selection

Furthermore, Sparkle handles various tasks for the user such as:

 * Algorithm meta information collection and statistics calculation
 * Instance/Data Set management and feature extraction
 * Compute cluster job submission and monitoring
 * Log file collection


## Installation

Sparkle is a Python based package, but requires several non-Python dependencies to run fully. The easiest installation is through Conda. A setup with Python virtual Environment is also possible, but requires more user input for the installation process.

### venv

Sparkle can also be installed as a standalone package using Pip. We recommend creating a new virtual environment with [venv](https://docs.python.org/3/library/venv.html) before to ensure no clashes between dependencies occur. Note that when creating a new venv, Sparkle needs Python 3.10 to run, so create your virtual environment with this Python version active

To install Sparkle in your virtual environment (in this example called 'venv' here) simply type:

```bash
python3 -m venv venv/

source venv/bin/activate  # Activate the new environment

pip install sparkle
```

Note that a direct installation through Pip does not handle certain dependencies of the Sparkle CLI, such as the required libraries for compiling [RunSolver](https://www.cril.univ-artois.fr/~roussel/runsolver/). This can possibly be resolved in your system (if it does not work 'out-of-the-box') by running `sudo yum install numactl-devel`.

You will need to supply, aside from the other dependencies in the next section, the following in your virtual environment:
- `Python 3.10` or greater is required to use Sparkle
- `libnuma` and `numactl` in order to compile RunSolver (Which can be installed through `sudo yum install numactl-devel`). We suggest to use `GCC 12.2.0`.

#### Sparkle Autocomplete

If you wish for the Bash autocomplete to also work for Sparkle's CLI commands, you can add the autocomplete script to your environments activation file. The source script of this can be found in `Resources/Other/venv_autocomplete.sh` and must be appended to your activation script, which can be done with the Sparkle CLI:

```bash
sparkle install autocomplete
```

Alternatively, if the installation fails for some reason or you are not using Venv,you can do it yourself with bash commands such as:

```bash
curl https://raw.githubusercontent.com/ADA-research/Sparkle/refs/heads/main/sparkle/Resources/Other/venv_autocomplete.sh >> venv/bin/activate
```

where `venv/bin/activate` leads to the script to activate your newly created environment. Note that afterwards you need to deactivate and reactivate the environment for changes to take effect. If you are using conda, you will probably need to append this script to your .bash_profile instead.

### Alternative: Conda

Sparkle can as alternatively be installed in a [Conda](https://docs.conda.io/en/latest/miniconda.html) environment. For this we provide an `environment.yml` file on [Github](https://github.com/ADA-research/Sparkle/blob/main/environment.yml), which you can download and run as follows:

```bash
wget https://raw.githubusercontent.com/ADA-research/Sparkle/main/environment.yml
```

and run:

```bash
conda env create -f environment.yml
```

The installation of the environment may take up to five minutes depending on your internet connection.
Once the environment has been created it can be activated by:

```bash
conda activate sparkle
```

You will need to reactivate the environment every time you start the terminal, before using Sparkle. Note that we generally recommend `venv` over `conda` as it is much lighter to run.

### Dependencies
Asside from several package dependencies, Sparkle's package / CLI relies on a few user supplied executables:
- `LaTex` compiler ([pdflatex](https://gist.github.com/rain1024/98dd5e2c6c8c28f9ea9d)) for report generation
- `Java`, tested with version 1.8.0_402, in order to use SMAC2
- `R` 4.3.1, in order to use IRACE

Other dependencies are handled by the Conda environment, but if that is not an option for you please ensure you have the following:

- [libnuma](https://anaconda.org/esrf-bcu/libnuma) and [numactl](https://anaconda.org/brown-data-science/numactl) for [Runsolver](http://www.cril.univ-artois.fr/~roussel/runsolver/) compilation which sparkle uses to measure solvers meta data. This is restricted to Linux based systems.
- [Swig](https://anaconda.org/conda-forge/swig/) 4.0.2 for [SMAC3](https://github.com/automl/SMAC3). Although Sparkle can be used without SMAC3, there seem to be some complications installation wise currently if swig is not present.

For detailed installation instructions see the documentation: https://ada-research.github.io/Sparkle/

### Developer installation

To install sparkle in development mode:
1. Pull the repository
2. Create a new Python venv and activate it, making sure it has the right Python version
3. Run, in the main directory of the repository, `pip install -e .[dev]`, to install dev dependencies alongside the package

#### Examples

See the `Examples` directory for some examples on how to use `Sparkle`. All Sparkle CLI commands need to be executed from the root of the initialised Sparkle directory.

#### Documentation

The documentation can be read at https://ada-research.github.io/Sparkle/. 

A `PDF` is also available in the [repository](https://raw.githubusercontent.com/ADA-research/Sparkle/main/Documentation/sparkle-userguide.pdf).

#### Licensing

Sparkle is distributed under the MIT licence

##### Component licences 

Sparkle is distributed with a number of external components, solvers, and instance sets. Descriptions and licensing information for each these are included in the `sparkle/Components` and `Examples/Resources/` directories.

The SATzilla 2012 feature extractor is used from `http://www.cs.ubc.ca/labs/beta/Projects/SATzilla/` with some modifications. The main modification of this component is to disable calling the SAT instance preprocessor called SatELite. It is located in: `Examples/Resources/Extractors/SAT-features-competition2012_revised_without_SatELite/`

### Citation

If you use Sparkle for one of your papers and want to cite it, please cite our [paper](https://doi.org/10.1109/TEVC.2022.3215013) describing Sparkle:
K. van der Blom, H. H. Hoos, C. Luo and J. G. Rook, **Sparkle: Toward Accessible Meta-Algorithmics for Improving the State of the Art in Solving Challenging Problems**, in _IEEE Transactions on Evolutionary Computation_, vol. 26, no. 6, pp. 1351-1364, Dec. 2022, doi: 10.1109/TEVC.2022.3215013.
```
@article{BloEtAl22,
  title={Sparkle: Toward Accessible Meta-Algorithmics for Improving the State of the Art in Solving Challenging Problems}, 
  author={van der Blom, Koen and Hoos, Holger H. and Luo, Chuan and Rook, Jeroen G.},
  journal={IEEE Transactions on Evolutionary Computation}, 
  year={2022},
  volume={26},
  number={6},
  pages={1351--1364},
  doi={10.1109/TEVC.2022.3215013}
}
```

### Maintainers
Thijs Snelleman,
Jeroen Rook,
Hadar Shavit,

### Contributors
Chuan Luo,
Richard Middelkoop,
Jérémie Gobeil,
Sam Vermeulen,
Marcel Baumann,
Jakob Bossek,
Tarek Junied,
Yingliu Lu,
Malte Schwerin,
Aaron Berger,
Marie Anastacio,
Aaron Berger,
Koen van der Blom,
Noah Peil,
Brian Schiller,
Emir Pisiciri

### Contact
sparkle@aim.rwth-aachen.de

### Sponsors

The development of Sparkle is partially sponsored by the [Alexander von Humboldt Foundation](https://www.humboldt-foundation.de/en/).
