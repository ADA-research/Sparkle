# Documentation system for Sparkle

To build the html documentation and the pdf documentation
```bash
make html latexpdf
```
The resulting documention are in `./build/*`.
The file `sparkle-doc.pdf` is a copy of the generated documentation in `build/latex`.

See `requirements.txt` file for requirements.

To clean up: `make clean`
