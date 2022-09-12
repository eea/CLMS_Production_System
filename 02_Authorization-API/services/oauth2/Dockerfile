FROM python:3.7

# Copies the requirements file to the Docker image
COPY requirements.txt .

# Install the remaining Python package required
RUN pip install -r requirements.txt

# Sets current working directory
WORKDIR /app

# Copies the application code to the current working directory
COPY src/ /app

