# Documentation system for Sparkle

Sparkle uses Sphinx to generate the documentation. The requirements are included in `../Documentation/requirments.txt`. LaTeX is also needed to build the `pdf` version of the documentation and userguide.

## Full documentation

To build the full html documentation
```bash
make html latexpdf
```
The resulting documentation is in `./build/html` with `./build/html/index.html` as the entry point.

The documentation can also be built in other formats, for example, `pdf` with 
```
make latexpdf
```

Consult the [Sphinx documentation](https://www.sphinx-doc.org) on how to use Sphinx.


## User Guide

A user guide is also availible in the file `sparkle-userguide.pdf`. To regenete the file, use  
```bash
make userguide
```

## Clean 

To clean up the generated files use
```bash
make clean
```
