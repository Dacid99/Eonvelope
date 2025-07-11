# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

source: Makefile
	python3 ../manage.py graph_models -a -g -o $(SOURCEDIR)/db_graph.svg
	python3 ../manage.py spectacular --validate --file $(SOURCEDIR)/api-schema.yml
	pydeps ../Emailkasten --max-bacon 2 -T svg -L ERROR --rankdir LR --no-show --cluster -o $(SOURCEDIR)/Emailkasten_import_graph.svg
	pydeps ../core --max-bacon 3 -T svg -L ERROR --rankdir LR --no-show --cluster -o $(SOURCEDIR)/core_import_graph.svg
	pydeps ../api --max-bacon 3 -T svg -L ERROR --rankdir LR --no-show --cluster -o $(SOURCEDIR)/api_import_graph.svg
	pydeps ../web --max-bacon 3 -T svg -L ERROR --rankdir LR --no-show --cluster -o $(SOURCEDIR)/web_import_graph.svg

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
