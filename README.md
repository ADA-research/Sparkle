Sparkle
=======


# About
Sparkle is a platform for the evaluation of empirical algorithms/solvers.


# Version
TBD


# License
TBD


# Authors
Chuan Luo,
Koen van der Blom,
Jeroen Rook,
Holger H. Hoos


# Contact
k.van.der.blom@liacs.leidenuniv.nl


# Licenses for components and examples packaged with Sparkle


AutoFolio license:
	`Components/AutoFolio-master/doc/license.rst`

ablation analysis license:
	`Components/ablationAnalysis-0.9.4/LICENSE.txt`

runsolver license:
	`Components/runsolver/src/LICENSE-GPL-3.0.txt`

smac license:
	`Components/smac-v2.10.03-master-778/LICENSE-AGPLv3.txt`

The SATzilla 2012 feature extractor is used from `http://www.cs.ubc.ca/labs/beta/Projects/SATzilla/` with some modifications. The main modification of this component is to disable calling the SAT instance preprocessor called SatELite. It is located in:	`Examples/Resources/Extractors/SAT-features-competition2012_revised_without_SatELite_sparkle/` and license of components are available in:

* `VARSAT/Main.C`
* `lp_solve_4.0/LICENSE`

# Instances
* The instances located in `Examples/Resources/Instances/SAT_test/` are taken from SATLIB (<https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html>)

* The instances located in `Examples/Resources/Instances/PTN/` and `Examples/Resources/Instances/PTN/2` are taken from <https://www.cs.utexas.edu/~marijn/ptn/> and <https://baldur.iti.kit.edu/sat-competition-2016/downloads/crafted16.zip>


# Solvers
* The solver `CSCCSat` located in `Examples/Resources/Solvers/CSCCSat/` is taken from <https://baldur.iti.kit.edu/sat-competition-2016/solvers/random/CSCCSat.zip>

* The solver `PbO-CCSAT` located in `Examples/Resources/Solvers/PbO-CCSAT-Generic/` is taken from <https://github.com/chuanluocs/PbO-CCSAT>

Unclear:


* `Examples/Resources/Solvers/MiniSAT/`
* `Examples/Resources/Solvers/VRP_SISRs/`
* `Examples/Resources/Solvers/Yahsp3/`
* `Examples/Resources/Instances/Depots/` + `test/train_few` subsets
* `Examples/Resources/Instances/X/` and `X2`



Components and examples provided as part of Sparkle:

* `Components/Sparkle-SAT-verifier/`
* `Components/Sparkle-latex-generator/`
* `Components/Sparkle-latex-generator-for-configuration/`
* `Components/Sparkle-latex-generator-for-test/`
