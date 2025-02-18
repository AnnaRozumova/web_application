lint:
	pipenv run pylint $(shell find . -name "*.py")

type-check:
	pipenv run mypy $(shell find . -name "*.py")

lint-all:
	pipenv run pylint $(shell find . -name "*.py")
	pipenv run mypy $(shell find . -name "*.py")

install-env:
	PIPENV_VENV_IN_PROJECT=1 pipenv install --dev

lock-env:
	pipenv lock

remove-env:
	pipenv --rm || echo "Environment not found"