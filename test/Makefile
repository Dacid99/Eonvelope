fulltest: pytest.ini .coveragerc
	pytest . | tee reports/fulltest.ansi

nofilterstest: pytest.ini .coveragerc
	pytest . --ignore=api/v1/filters | tee reports/nofilterstest.ansi
