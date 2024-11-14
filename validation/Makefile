lint: pylintrc
	pylint --rcfile=$< ../Emailkasten

strictlint: pylintrc_strict
	pylint --rcfile=$< ../Emailkasten

check: mypy.ini
	mypy --config-file $< Emailkasten/