.DEFAULT_GOAL := all

bandit:
	poetry run bandit -r . -x ./src/app/tests
toml_sort:
	poetry run toml-sort pyproject.toml --all --in-place
flake8:
	poetry run flake8 .
isort:
	poetry run isort .
pylint:
	poetry run pylint app --extension-pkg-whitelist='pydantic'
black:
	poetry run black .
mypy:
	poetry run mypy --install-types --non-interactive .
test:
	poetry run pytest
lint: flake8 isort pylint black mypy toml_sort
