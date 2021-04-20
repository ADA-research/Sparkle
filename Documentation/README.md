# Documentation system for Sparkle

Sparkle use Sphinx to generate its documentation. The requirements are included in `../requirments_first.txt`. 

## Full documentation

To build the full html documentation
```bash
make html latexpdf
```
The resulting documentation is in `./build/html` with `./build/html/index.html` as entry point.

The documentation can also be build in other format, for example `pdf` with 
```
make latexpdf
```

## User Guide

A user guide can also be build using 
```bash
make userguide
```

That will generate the file `sparkle-userguide.pdf`. For easy consultation, an up-to-date file should be include in the directory. 

## Clean 

To clean up the generated files
```bash
make clean
```
