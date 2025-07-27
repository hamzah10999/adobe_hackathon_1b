# Use a minimal official Python image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    build-essential \
    libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app

# Make setup.sh executable
RUN chmod +x setup.sh

# Run setup.sh (installs deps + downloads model)
RUN ./setup.sh

# Allow user to override command at runtime
ENTRYPOINT ["python", "main.py"]
