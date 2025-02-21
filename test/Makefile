fulltest: pytest.ini
	pytest . | tee reports/fulltest.ansi

nofilterstest: pytest.ini
	pytest . --ignore=filters | tee reports/nofilterstest.ansi
