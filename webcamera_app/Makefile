lint:
	pipenv run pylint $(shell find . -name "*.py")

type-check:
	pipenv run mypy $(shell find . -name "*.py")

lint-all:
	pipenv run pylint $(shell find . -name "*.py")
	pipenv run mypy $(shell find . -name "*.py")

test:
	python -m pytest --cov=webcamera_app

coverage:
	python -m pytest --cov=webcamera_app --cov-report=html

serve:
	cd htmlcov && python3 -m http.server 8000

install-env:
	PIPENV_VENV_IN_PROJECT=1 pipenv install --dev

lock-env:
	pipenv lock

remove-env:
	pipenv --rm || echo "Environment not found"