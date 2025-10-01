# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SOURCEDIR     = source
USERGUIDEDIR  = source/userguide
BUILDDIR      = build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help makefile

apidoc: 
	sphinx-apidoc -f -o source/_generated ../src/sparkle/CLI

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: makefile apidoc
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

userguide: makefile
	@$(SPHINXBUILD) -M latexpdf "$(SOURCEDIR)/userguide" "$(BUILDDIR)/userguide" $(SPHINXOPTS) $(O)
	cp "$(BUILDDIR)/userguide/latex/sparkle-userguide.pdf" sparkle-userguide.pdf

clean: makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	rm -f $(SOURCEDIR)/_generated/*

all: userguide html;
