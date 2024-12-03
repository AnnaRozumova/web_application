FROM python:3.11-slim

WORKDIR /app

RUN pip install --upgrade pip && pip install pipenv

COPY Pipfile Pipfile.lock ./

RUN pipenv install --system --deploy

COPY wiki_app.py ./

EXPOSE 8000

CMD ["python", "wiki_app.py"]
