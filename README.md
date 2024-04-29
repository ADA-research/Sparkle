# Sparkle

Sparkle is a Programming by Optimisation (PbO)-based problem-solving platform designed to enable the widespread and effective use of PbO techniques for improving the state-of-the-art in solving a broad range of prominent AI problems, including SAT and AI Planning.

Specifically, Sparkle facilitates the use of:

 * Automated algorithm configuration
 * Automated algorithm selection

## Installation

The installation process use the `conda` package manager (to install https://docs.conda.io/en/latest/miniconda.html`). 

### Get a copy of Sparkle
To get a copy of Sparkle you can clone the repository using `git`.
``` bash
  $ git clone https://github.com/ADA-research/Sparkle
```


### Install dependencies

Sparkle depends on Python 3.9+, swig 3.0, gnuplot, LaTeX, and multiple Python packages. LaTeX is used to create the reports, if you want to use this functionality you will need to install it manually.

The rest of the dependencies can installed and activated with

``` bash
  $ conda env create -f environment.yml
  $ conda activate sparkle
```

For detailed installation instructions see the documentation: https://sparkle-ai.readthedocs.io/

## Examples

See the `Examples` directory for some examples on how to use `Sparkle`. All commands need to be executed from the root directory. 

## Documentation

The documentation can be read at https://sparkle-ai.readthedocs.io/. 

A `PDF` is also available in the repository at [Documentation/sparkle-userguide.pdf](./Documentation/sparkle-userguide.pdf).

## Licensing

Sparkle is distributed under the MIT licence

### Component licences 

Sparkle is distributed with a number of external components, solvers, and instance sets. Descriptions and licensing information for each these are included in the `Components/` and `Examples/Resources/` directories.

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
Marie Anastacio,
Koen van der Blom

## Contact
sparkle@aim.rwth-aachen.de

