REPORT_PATH=reports/

pylint-code: pylintrc_src
	poetry run pylint --rcfile=$< ../src | tee $(REPORT_PATH)pylint_code.ansi

pylint-docs: pylintrc_docs
	poetry run pylint --rcfile=$< ../src | tee $(REPORT_PATH)pylint_docs.ansi

pylint-test: pylintrc_test
	poetry run pylint --rcfile=$< ../test/ | tee $(REPORT_PATH)pylint_test.ansi

ruff: ruff.toml
	poetry run ruff check --config=$< ../src/ ../test/ | tee $(REPORT_PATH)ruff.ansi

djlint: djlintrc
	poetry run djlint --configuration $< ../src/web/templates | tee $(REPORT_PATH)djlint.ansi

mypy: mypy.ini
	poetry run mypy --config-file $< ../src/ | tee $(REPORT_PATH)mypy/mypy.ansi

dmypy-start: mypy.ini
	poetry run dmypy run --log-file $(REPORT_PATH)mypy/dmypy.log -- --config-file $< ../src/ | tee $(REPORT_PATH)mypy/dmypy.ansi

dmypy-check:
	poetry run dmypy recheck | tee $(REPORT_PATH)mypy/dmypy.ansi

autotyping:
	poetry run python3 -m autotyping --safe ../src/

doc8: doc8.ini
	poetry run doc8 --config doc8.ini ../docs/source/rst/ | tee $(REPORT_PATH)doc8.ansi

codespell: .codespellrc
	poetry run codespell ../src ../test/ ../docs/ ../.gitea/ ../.github/ ../.gitlab/ ../*.md --config=$< | tee $(REPORT_PATH)codespell.ansi

eslint:
	npx --yes eslint --no-config-lookup --fix

hadolint:
	docker run --rm -i hadolint/hadolint < docker/Dockerfile | tee $(REPORT_PATH)hadolint.ansi

licenses:
	pip-licenses --from=all --with-license-file --format=plain-vertical --no-license-path > ../THIRD_PARTY_LICENSES

clean:
	rm -rf $(REPORT_PATH)*
