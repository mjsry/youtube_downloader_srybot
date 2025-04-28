# Use official Python slim image
FROM python:3.11-slim

# Install ffmpeg and other dependencies
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

# Set work directory
WORKDIR /app

# Copy requirements first (to cache install)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Set the command to run your bot
CMD ["python", "main.py"]
