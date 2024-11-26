FROM python:3.11-slim

WORKDIR /app

RUN pip install --upgrade pip && pip install pipenv

COPY Pipfile Pipfile.lock ./

RUN pipenv install --system --deploy

COPY main.py ./
COPY templates /app/templates

EXPOSE 8000

CMD ["python", "main.py"]
