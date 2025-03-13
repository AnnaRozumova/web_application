lint:
	pipenv run pylint wiki_app.py

type-check:
	pipenv run mypy wiki_app.py

lint-all:
	pipenv run pylint wiki_app.py
	pipenv run mypy wiki_app.py

test:
	pipenv run pytest tests/

install-env:
	PIPENV_VENV_IN_PROJECT=1 pipenv install --dev

lock-env:
	pipenv lock

remove-env:
	pipenv --rm || echo "Environment not found"