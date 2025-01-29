# Use Python 3.11 slim image as the base
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for OpenCV and Pipenv
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip && pip install pipenv

COPY Pipfile Pipfile.lock ./

# Install dependencies in system mode (outside of virtualenv)
RUN pipenv install --system --deploy

# Copy the application code
COPY webcamera_app.py ./
COPY camera_controller.py ./
COPY s3_handler.py ./

# Expose the application port
EXPOSE 5454

# Run the application directly with Python
CMD ["python", "webcamera_app.py"]

