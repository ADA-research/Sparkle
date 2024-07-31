# Sparkle

Sparkle is a Programming by Optimisation (PbO)-based problem-solving platform designed to enable the widespread and effective use of PbO techniques for improving the state-of-the-art in solving a broad range of prominent AI problems, including SAT and AI Planning.

Specifically, Sparkle facilitates the use of:

 * Automated algorithm configuration
 * Automated algorithm selection

## Installation

The Sparkle package can be installed using Pip. We recommend creating a new virtual environment (For example, [PyEnv](https://github.com/pyenv/pyenv)) before to ensure no clashes between dependencies occur. 

```bash
    $ pip install SparkleAI
```

Alternatively, to be able to fully use the Command Line Interface (CLI) of Sparkle, a Conda environment is required (For Conda installation see [here]( https://docs.conda.io/en/latest/miniconda.html)). Simply download the `environment.yml` file from the Github and run:

```bash
    $ conda env create -f environment.yml
```

And afterwards activated by:

```bash
    $ conda activate sparkle
```

Note that the creation of the Conda environment also takes care of the installation of Sparkle itself.

### Install dependencies
Asside from several package dependencies, Sparkle's package / CLI relies on a few user supplied executables:
- `LaTex` compiler ([pdflatex](https://gist.github.com/rain1024/98dd5e2c6c8c28f9ea9d)) for report generation
- `Java`, tested with version 1.8.0_402, in order to use SMAC2

Other dependencies are handled by the Conda environment, but if that is not an option for you please ensure you have the following:

- [libnuma](https://anaconda.org/esrf-bcu/libnuma) and [numactl](https://anaconda.org/brown-data-science/numactl) for [Runsolver](http://www.cril.univ-artois.fr/~roussel/runsolver/) compilation which sparkle uses to measure solvers meta data. This is restricted to Linux based systems.
- [Swig](https://anaconda.org/conda-forge/swig/) 4.0.2 for [SMAC3](https://github.com/automl/SMAC3), which is in turn used by [AutoFolio](https://github.com/automl/AutoFolio).

For detailed installation instructions see the documentation: https://sparkle-ai.readthedocs.io/

## Examples

See the `Examples` directory for some examples on how to use `Sparkle`. All Sparkle CLI commands need to be executed from the root of the initialised Sparkle directory.

## Documentation

The documentation can be read at https://sparkle-ai.readthedocs.io/. 

A `PDF` is also available in the repository at [Documentation/sparkle-userguide.pdf](./Documentation/sparkle-userguide.pdf).

## Licensing

Sparkle is distributed under the MIT licence

### Component licences 

Sparkle is distributed with a number of external components, solvers, and instance sets. Descriptions and licensing information for each these are included in the `sparkle/Components` and `Examples/Resources/` directories.

The SATzilla 2012 feature extractor is used from `http://www.cs.ubc.ca/labs/beta/Projects/SATzilla/` with some modifications. The main modification of this component is to disable calling the SAT instance preprocessor called SatELite. It is located in: `Examples/Resources/Extractors/SAT-features-competition2012_revised_without_SatELite_sparkle/`

## Citation

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


## Maintainers
Thijs Snelleman,
Jeroen Rook,
Holger H. Hoos,
Noah Peil,
Brian Schiller

## Contributors
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
Koen van der Blom

## Contact
sparkle@aim.rwth-aachen.de

