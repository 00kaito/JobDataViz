FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker caching
COPY pyproject.toml ./
RUN pip install -U pip setuptools wheel

# Install Python dependencies
RUN pip install \
    dash \
    dash-bootstrap-components \
    plotly \
    pandas \
    numpy \
    flask \
    flask-sqlalchemy \
    flask-login \
    flask-wtf \
    wtforms \
    email-validator \
    werkzeug \
    gunicorn \
    psycopg2-binary

# Copy application files
COPY . .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Start command
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "main:server"]