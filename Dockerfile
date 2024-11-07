FROM python:3.11.10-slim

WORKDIR /app

RUN pip install --upgrade pip && pip install pipenv
COPY ./Pipfile ./Pipfile.lock ./
RUN pipenv install --system --deploy

COPY main.py ./
COPY templates/ templates/
COPY static/ static/

EXPOSE 5000

CMD ["python", "main.py"]