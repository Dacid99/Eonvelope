codelint: pylintrc_src
	pylint --rcfile=$< ../Emailkasten ../core/ ../api/ ../web/ | tee reports/pylint_code.ansi

docslint: pylintrc_docs
	pylint --rcfile=$< ../Emailkasten ../core/ ../api/ ../web/ | tee reports/pylint_docs.ansi

testlint: pylintrc_test
	pylint --rcfile=$< ../test/ | tee reports/pylint_test.ansi

rufflint: ruff.toml
	ruff check --config=$< ../Emailkasten ../core/ ../api/ ../web/ ../test/ | tee reports/ruff.ansi

templatelint: djlintrc
	djlint --configuration djlintrc ../web/templates | tee -a reports/htmllint.ansi

mypy-check: mypy.ini
	export SECRET_KEY='something'
	mypy --config-file $< ../Emailkasten ../core/ ../api/ ../web/ | tee reports/mypy/mypy.ansi

dmypy-start: mypy.ini
	export SECRET_KEY='something'
	dmypy run --log-file reports/mypy/dmypy.log -- --config-file $< ../Emailkasten ../core/ ../api/ ../web/ | tee reports/mypy/mypy.ansi

dmypy-check:
	dmypy recheck | tee reports/mypy/mypy.ansi

types:
	python3 -m autotyping --safe ../Emailkasten ../core/ ../api/ ../web/

spelling: .codespellrc
	codespell ../Emailkasten/ ../core/ ../api/ ../web/ ../test/ ../docs/ ../.gitea/ ../.github/ ../.gitlab/ ../*.md --config=$< | tee reports/codespell.ansi

clean:
	rm -f reports/* ../docs/build/html/mypy_report/*
