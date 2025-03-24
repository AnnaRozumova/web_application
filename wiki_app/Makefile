lint:
	pipenv run pylint wiki_app.py

type-check:
	pipenv run mypy wiki_app.py

lint-all:
	pipenv run pylint wiki_app.py
	pipenv run mypy wiki_app.py

test:
	pipenv run pytest --cov=wiki_app

coverage:
	pipenv run pytest --cov=wiki_app --cov-report=html

serve:
	cd htmlcov && python3 -m http.server 8000

install-env:
	PIPENV_VENV_IN_PROJECT=1 pipenv install --dev

lock-env:
	pipenv lock

remove-env:
	pipenv --rm || echo "Environment not found"