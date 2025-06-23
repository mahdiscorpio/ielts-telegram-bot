# Use an official Python base image
FROM python:3.12-slim

# Set working directory in the container
WORKDIR /app

# Copy requirements and install
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your project
COPY . .

# Run your bot when the container starts
CMD ["python3", "src/main.py"]
