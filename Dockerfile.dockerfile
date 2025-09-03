# F1 Results Scraper - Docker Configuration
# ==========================================

FROM python:3.11-slim

# Set metadata
LABEL maintainer="vanshjain081203@gmail.com"
LABEL description="Professional F1 Results Scraper"
LABEL version="2.0.0"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY f1_scraper_pro.py .
COPY config/ ./config/

# Create output directory
RUN mkdir -p output logs

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash f1user \
    && chown -R f1user:f1user /app

USER f1user

# Set environment variables
ENV PYTHONPATH=/app
ENV F1_OUTPUT_DIR=/app/output
ENV F1_LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import f1_scraper_pro; print('OK')" || exit 1

# Default command
CMD ["python", "f1_scraper_pro.py", "--summary"]