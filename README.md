# Sparkle

Sparkle allows everyone to use AutoAI and create efficient, correct and reproducible experiments.

Sparkle is a Programming by Optimisation (PbO)-based problem-solving platform designed to enable the widespread and effective use of PbO techniques for improving the state-of-the-art in solving a broad range of prominent AI problems, including SAT and AI Planning.

Sparkle offers a consistent platform to design and run experiments on:

 * Algorithm configuration
 * Algorithm comparison
 * Algorith contribution to selector
 * Selector comparison

## Usage

To use Sparkle, clone it using Git. All files and results will be produced in that directory. 

All commands need to be run from this cloned root directory. See `Examples` for some examples. 

## Documentation

The documentation is in the `Documentation` directory. A `pdf` is available and the `html` documentation can be generated.

## Contact
k.van.der.blom@liacs.leidenuniv.nl

## Licenses

Sparkle is distributed under the MIT licence

### Component licences 

Sparkle is bundled with some external components that are distributed with their own licence.


* AutoFolio: `Components/AutoFolio-master/doc/license.rst`
* Ablation analysis: `Components/ablationAnalysis-0.9.4/LICENSE.txt`
* runsolver: `Components/runsolver/src/LICENSE-GPL-3.0.txt`
* smac:	`Components/smac-v2.10.03-master-778/LICENSE-AGPLv3.txt`
* SATzilla 2012:`Examples/Resources/Extractors/SAT-features-competition2012_revised_without_SatELite_sparkle/{VARSAT/Main.C, lp_solve_4.0/LICENSE}`

The SATzilla 2012 feature extractor is used from `http://www.cs.ubc.ca/labs/beta/Projects/SATzilla/` with some modifications. The main modification of this component is to disable calling the SAT instance preprocessor called SatELite. It is located in: `Examples/Resources/Extractors/SAT-features-competition2012_revised_without_SatELite_sparkle/`

## Components

### Instances
* The instances located in `Examples/Resources/Instances/SAT_test/` are taken from SATLIB (<https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html>)

* The instances located in `Examples/Resources/Instances/PTN/` and `Examples/Resources/Instances/PTN/2` are taken from <https://www.cs.utexas.edu/~marijn/ptn/> and <https://baldur.iti.kit.edu/sat-competition-2016/downloads/crafted16.zip>

### Solvers
* The solver `CSCCSat` located in `Examples/Resources/Solvers/CSCCSat/` is taken from <https://baldur.iti.kit.edu/sat-competition-2016/solvers/random/CSCCSat.zip>

* The solver `PbO-CCSAT` located in `Examples/Resources/Solvers/PbO-CCSAT-Generic/` is taken from <https://github.com/chuanluocs/PbO-CCSAT>


### To be determined

* `Examples/Resources/Solvers/MiniSAT/`
* `Examples/Resources/Solvers/VRP_SISRs/`
* `Examples/Resources/Instances/X/` and `X2`

### Components and examples provided as part of Sparkle:

* `Components/Sparkle-SAT-verifier/`
* `Components/Sparkle-latex-generator/`
* `Components/Sparkle-latex-generator-for-configuration/`
* `Components/Sparkle-latex-generator-for-test/`

## Authors
Chuan Luo,
Koen van der Blom,
Jeroen Rook,
Holger H. Hoos
Jeremie Gobeil
