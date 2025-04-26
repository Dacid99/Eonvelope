codelint: pylintrc_code
	pylint --rcfile=$< ../Emailkasten ../core/ ../api/ ../web/ | tee reports/pylint_code.ansi

docslint: pylintrc_docs
	pylint --rcfile=$< ../Emailkasten ../core/ ../api/ ../web/ | tee reports/pylint_docs.ansi

testlint: pylintrc_test
	pylint --rcfile=$< ../test/ | tee reports/pylint_test.ansi

rufflint: ruff.toml
	ruff check --config=$< ../Emailkasten ../core/ ../api/ ../web/ ../test/ | tee reports/ruff.ansi

templatelint: djlintrc
	djlint --configuration djlintrc ../web/templates | tee -a reports/htmllint.ansi

check: mypy.ini
	mypy --config-file $< ../Emailkasten ../test/ ../core/ ../api/ ../web/ | tee reports/mypy/mypy.ansi

types:
	python3 -m autotyping --safe ../Emailkasten ../core/ ../api/ ../web/

clean:
	rm -f reports/* ../docs/build/html/mypy_report/*
