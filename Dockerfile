# Use official Python slim image for smaller size
FROM python:3.11-slim

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TRANSFORMERS_CACHE=/tmp/.cache

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
# Clean up any old Python cache files
RUN find . -type d -name "__pycache__" -exec rm -r {} + || true
RUN find . -type f -name "*.pyc" -delete || true
# Uninstall all possible supabase-related packages before install
RUN pip uninstall -y supabase postgrest-py gotrue postgrest supabase_py || true
# Add a dummy build arg to force cache busting
ARG CACHEBUST=1
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Expose port for FastAPI
EXPOSE 7860

# Command to run the app with Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"] 