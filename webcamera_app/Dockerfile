FROM python:3.11.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && pip install pipenv
COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy

COPY app.py /app/app.py
COPY templates /app/templates


EXPOSE 5454

CMD ["python", "/app/app.py"]