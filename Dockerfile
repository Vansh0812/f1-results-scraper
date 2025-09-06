# F1 Results Scraper - Fixed Dockerfile
# =====================================
# This version only copies files that actually exist in your repo

FROM python:3.11-slim

# Set metadata
LABEL maintainer="your.email@example.com"
LABEL description="Professional F1 Results Scraper"
LABEL version="2.0.0"

# Set working directory
WORKDIR /app

# Install system dependencies (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy ONLY the files that exist in your repo
COPY f1_scraper_pro.py .

# Create directories that the app needs
RUN mkdir -p output logs

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash f1user && \
    chown -R f1user:f1user /app

USER f1user

# Set environment variables
ENV PYTHONPATH=/app
ENV F1_OUTPUT_DIR=/app/output
ENV F1_LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from f1_scraper_pro import F1ResultsScraperPro; print('OK')" || exit 1

# Default command
CMD ["python", "f1_scraper_pro.py", "--summary"]