# Use the latest Python 3.11 slim image
FROM python:3.11-slim

WORKDIR /app

# Install Pipenv and other system dependencies
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip && pip install pipenv

# Copy Pipfile and Pipfile.lock
COPY ../Pipfile ../Pipfile.lock ./

# Install dependencies with Pipenv in system mode
RUN pipenv install --system --deploy

# Copy the application code
COPY db_app/db_app.py ./

# Expose port for db_app microservice
EXPOSE 5001

# Run Flask without relying on Pipenv's virtual environment
CMD ["python", "db_app.py"]

