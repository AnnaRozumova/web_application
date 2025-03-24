lint:
	pipenv run pylint main.py || [ $$? -lt 32 ]

type-check:
	pipenv run mypy main.py

lint-all:
	pipenv run pylint main.py
	pipenv run mypy main.py

test:
	pipenv run pytest --cov=main_app

coverage:
	pipenv run pytest --cov=main_app --cov-report=html

serve:
	cd htmlcov && python3 -m http.server 8000

install-env:
	PIPENV_VENV_IN_PROJECT=1 pipenv install --dev

lock-env:
	pipenv lock

remove-env:
	pipenv --rm || echo "Environment not found"