# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= poetry run sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

# Put it first so that "make" without argument is like "make help".
help:
	$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

source: Makefile
	poetry run python3 ../manage.py graph_models -a -g -o $(SOURCEDIR)/db_graph.svg
	poetry run python3 ../manage.py spectacular --file $(SOURCEDIR)/api-schema.yml
	poetry run pydeps ../config --max-bacon 2 -T svg -L ERROR --rankdir LR --no-show --cluster -o $(SOURCEDIR)/config_import_graph.svg
	poetry run pydeps ../eonvelope --max-bacon 2 -T svg -L ERROR --rankdir LR --no-show --cluster -o $(SOURCEDIR)/eonvelope_import_graph.svg
	poetry run pydeps ../core --max-bacon 3 -T svg -L ERROR --rankdir LR --no-show --cluster -o $(SOURCEDIR)/core_import_graph.svg
	poetry run pydeps ../api --max-bacon 3 -T svg -L ERROR --rankdir LR --no-show --cluster -o $(SOURCEDIR)/api_import_graph.svg
	poetry run pydeps ../web --max-bacon 3 -T svg -L ERROR --rankdir LR --no-show --cluster -o $(SOURCEDIR)/web_import_graph.svg

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

clear: Makefile
	rm -rf build/*
