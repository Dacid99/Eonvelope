fulltest: pytest.ini
	pytest . | tee reports/fulltest.ansi

nofilterstest: pytest.ini
	pytest . --ignore=api/v1/filters | tee reports/nofilterstest.ansi
