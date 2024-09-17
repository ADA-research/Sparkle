# Quick Start

The Sparkle package offers an extensive _Command Line Interface_ (CLI) to allow for easy interaction with the platform. If you haven't installed the package already, see the {ref}`Install Sparkle <quick-install>` page.

```{note}
Sparkle currently relies on [Slurm](https://slurm.schedmd.com/), but in some cases works locally as well.
Sparkle also relies on [RunSolver](http://www.cril.univ-artois.fr/~roussel/runsolver/), which is a Linux based program. Thus Sparkle can only run on Linux based systems in many cases.
```

To initialise a new Sparkle platform, select a (preferably new / empty) directory, and run in the terminal:
```shell
sparkle initialise
```

This sets up various default directories and files for Sparkle to use that you can customise later. Note that if you wish to download the files for the {ref}`Examples <examples>`, you can run the command with the flag:

```shell
sparkle initialise --download-examples
```

Due to the examples containing various algorithms and their executables, but also entire datasets, it is about 300MB large. Now you might receive a few warnings during the inialisation, lets go through a few of them:

* _"Could not find Java as an executable"_: One of the algorithm configurators Sparkle has to offer (SMAC2) is build on Java. Make sure your system has Java version 1.8.0_402 installed.
* _"RunSolver was not compiled succesfully"_: Sparkle uses RunSolver to monitor algorithms and their meta statistics, such as CPU and Wallclock time. RunSolver needs various libraries to be compiled. You can run the make file in the Sparkle package components section (sparkle/Components/runsolver/src/Makefile) to inspect what your system is missing for the compilation to work.