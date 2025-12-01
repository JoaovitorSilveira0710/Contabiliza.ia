# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create directories for storage and backups
RUN mkdir -p storage backups

# Collect static files (if needed)
RUN cd django_backend && python manage.py collectstatic --noinput || true

# Expose port
EXPOSE 8000

# Run migrations and start server
CMD cd django_backend && \
    python manage.py makemigrations && \
    python manage.py migrate && \
    python manage.py runserver 0.0.0.0:8000
