codelint: pylintrc_code
	pylint --rcfile=$< ../Emailkasten ../test/ | tee reports/pylint_code.txt

docslint: pylintrc_docs
	pylint --rcfile=$< ../Emailkasten ../test/ | tee reports/pylint_docs.txt

stylelint: pylintrc_style
	pylint --rcfile=$< ../Emailkasten ../test/| tee reports/pylint_style.txt

check: mypy.ini
	mypy --config-file $< ../Emailkasten/ ../test/

clean:
	rm -f reports/* ../docs/mypy_report.html ../docs/*.svg
