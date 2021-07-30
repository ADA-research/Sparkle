# Sparkle

Sparkle is a Programming by Optimisation (PbO)-based problem-solving platform designed to enable the widespread and effective use of PbO techniques for improving the state-of-the-art in solving a broad range of prominent AI problems, including SAT and AI Planning.

Specifically, Sparkle facilitates the use of:

 * Automated algorithm configuration
 * Automated algorithm selection

## Usage

To use Sparkle, clone it using Git and follow the installation instructions provided under `Examples/installation.md`. All files and results will be produced under the main Sparkle directory. 

All commands need to be executed from this cloned root directory. See the `Examples` directory for some examples. 

## Documentation

The documentation can be found in the `Documentation` directory. A `PDF` is available at `Documentation/sparkle-userguide.pdf` and the `HTML` documentation can be generated.

## Licensing

Sparkle is distributed under the MIT licence

### Component licences 

Sparkle is distributed with a number of external components, solvers, and instance sets. Descriptions and licensing information for each these are included in the `Components/` and `Examples/Resources/` directories.

The SATzilla 2012 feature extractor is used from `http://www.cs.ubc.ca/labs/beta/Projects/SATzilla/` with some modifications. The main modification of this component is to disable calling the SAT instance preprocessor called SatELite. It is located in: `Examples/Resources/Extractors/SAT-features-competition2012_revised_without_SatELite_sparkle/`

## Authors
Chuan Luo,
Koen van der Blom,
Jeroen Rook,
Holger H. Hoos,
Richard Middelkoop,
Jeremie Gobeil

## Contact
k.van.der.blom@liacs.leidenuniv.nl

