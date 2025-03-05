# _Sparkle_

[![Tests](https://ada-research.github.io/Sparkle/_static/junit/junit-badge.svg)](https://ada-research.github.io/Sparkle/_static/junit/index.html)
![tests status](https://github.com/ada-research/sparkle/actions/workflows/unittest.yml/badge.svg?event=push)
[![Coverage Status](https://ada-research.github.io/Sparkle/_static/coverage/coverage-badge.svg)](https://ada-research.github.io/Sparkle/_static/coverage/index.html)
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

Sparkle is a Python based package, but required several non-Python dependencies to run fully. The easiest installation is through Conda. A setup with Python virtual Environment is also possible, but requires more user input for the installation process.

### Conda

The quick and full installation of Sparkle can be done using Conda (For Conda installation see [here]( https://docs.conda.io/en/latest/miniconda.html)). 

Simply download the `environment.yml` file from the [Github](https://github.com/ADA-research/Sparkle/blob/main/environment.yml) with wget:

```bash
wget https://raw.githubusercontent.com/ADA-research/Sparkle/main/environment.yml
```

and run:

```bash
conda env create -f environment.yml
```

The installation of the environment may take up to five minutes depending on your internet connection.
Once the environment has been created it can be activated by:

```
conda activate sparkle
```

```{note}
The creation of the Conda environment also takes care of the installation of the Sparkle package itself. 
```

```{note}
You will need to reactivate the environment every time you start the terminal, before using Sparkle.
```

### venv

Sparkle can also be installed as a standalone package using Pip. We recommend creating a new virtual environment with [venv](https://docs.python.org/3/library/venv.html) before to ensure no clashes between dependencies occur. Note that when creating a new venv, Sparkle needs Python 3.10 to run, so create your virtual environment with this Python version active

To install Sparkle in the virtual environment simply type:

```bash
pip install SparkleAI
```

Note that a direct installation through Pip does not handle certain dependencies of the Sparkle CLI, such as the required libraries for compiling [RunSolver](https://www.cril.univ-artois.fr/~roussel/runsolver/).

You will need to supply, asside from the other dependencies in the next section, the following in your virtual environment:
- `Python 3.10` is required to use Sparkle
- `libnuma` and `numactl` in order to compile RunSolver. We suggest to use `GCC 12.2.0`.

### Bash autocomplete

If you wish for the Bash autocomplete to also work for Sparkle's CLI commands, you can type `sparkle install autocomplete`, which will append a single line of code to your `.bash_profile` allowing you to auto complete any sparkle command with the tab.

### Dependencies
Asside from several package dependencies, Sparkle's package / CLI relies on a few user supplied executables:
- `LaTex` compiler ([pdflatex](https://gist.github.com/rain1024/98dd5e2c6c8c28f9ea9d)) for report generation
- `Java`, tested with version 1.8.0_402, in order to use SMAC2
- `R` 4.3.1, in order to use IRACE

Other dependencies are handled by the Conda environment, but if that is not an option for you please ensure you have the following:

- [libnuma](https://anaconda.org/esrf-bcu/libnuma) and [numactl](https://anaconda.org/brown-data-science/numactl) for [Runsolver](http://www.cril.univ-artois.fr/~roussel/runsolver/) compilation which sparkle uses to measure solvers meta data. This is restricted to Linux based systems.
- [Swig](https://anaconda.org/conda-forge/swig/) 4.0.2 for [SMAC3](https://github.com/automl/SMAC3).

For detailed installation instructions see the documentation: https://ada-research.github.io/Sparkle/

### Developer installation

The file `dev-env.yml` is used for developer mode of the Sparkle package and contains several extra packages for testing.

The two environments can be created in parallel since one is named `sparkle` and the other `sparkle-dev`. If you want to update an environment it is better to do a clean installation by removing and recreating it. For example:

```
conda deactivate
conda env remove -n sparkle
conda env create -f environment.yml
conda activate sparkle
```

This should be fast as both `conda` and `pip` use local cache for the packages.

#### Examples

See the `Examples` directory for some examples on how to use `Sparkle`. All Sparkle CLI commands need to be executed from the root of the initialised Sparkle directory.

#### Documentation

The documentation can be read at https://ada-research.github.io/Sparkle/. 

A `PDF` is also available in the [repository](https://raw.githubusercontent.com/ADA-research/Sparkle/main/Documentation/sparkle-userguide.pdf).

#### Licensing

Sparkle is distributed under the MIT licence

##### Component licences 

Sparkle is distributed with a number of external components, solvers, and instance sets. Descriptions and licensing information for each these are included in the `sparkle/Components` and `Examples/Resources/` directories.

The SATzilla 2012 feature extractor is used from `http://www.cs.ubc.ca/labs/beta/Projects/SATzilla/` with some modifications. The main modification of this component is to disable calling the SAT instance preprocessor called SatELite. It is located in: `Examples/Resources/Extractors/SAT-features-competition2012_revised_without_SatELite_sparkle/`

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
Holger H. Hoos,

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
Aaron Berger
Koen van der Blom,
Noah Peil,
Brian Schiller,
Emir Pisiciri

### Contact
sparkle@aim.rwth-aachen.de


### Sponsors

The development of Sparkle is partially sponsored by the [Alexander von Humboldt foundation](https://www.humboldt-foundation.de/en/).
