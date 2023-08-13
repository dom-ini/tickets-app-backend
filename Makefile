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
unit:
	poetry run pytest app/tests/unit
integration:
	poetry run pytest app/tests/integration
lint: black flake8 isort pylint mypy toml_sort
