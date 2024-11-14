# Use Python 3.11 slim image as the base
FROM python:3.11-slim

WORKDIR /app

# Upgrade pip and install pipenv
RUN pip install --upgrade pip && pip install pipenv

COPY Pipfile Pipfile.lock ./

# Install dependencies in system mode (outside of virtualenv)
RUN pipenv install --system --deploy

# Copy the application code and directories
COPY main.py ./
COPY templates/ templates/
COPY static/ static/

# Expose port 5000 for the Flask app
EXPOSE 5000

# Run the application directly with Python
CMD ["python", "main.py"]

