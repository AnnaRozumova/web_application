# Use Python 3.11 slim image as the base
FROM python:3.11-slim

WORKDIR /app

# Upgrade pip and install pipenv
RUN pip install --upgrade pip && pip install pipenv

# Copy Pipfile and Pipfile.lock from the root directory
COPY ../Pipfile ../Pipfile.lock ./

# Install dependencies in system mode (outside of virtualenv)
RUN pipenv install --system --deploy

# Copy the application code and directories
COPY main_app/main.py ./
COPY main_app/templates/ templates/
COPY main_app/static/ static/

# Expose port 5000 for the Flask app
EXPOSE 5000

# Run the application directly with Python
CMD ["python", "main.py"]

