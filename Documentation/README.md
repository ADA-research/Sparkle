# Documentation system for Sparkle

## Requirements
* spinx
* recommondmark

## Build

build the html documentation and the pdf
```bash
make html latexpdf
```

The resulting documention are in `./build/*`.

To clean up: `make clean`


## Generate the apidoc

The api documention is not parses antomatically. This command need to be run to 
reparse the code and generate the up-to-date api documentation files.

```bash
sphinx-apidoc -f -o source/ ../Commands
```