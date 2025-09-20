# Multi-stage build for optimized production image
FROM python:3.11-slim as builder

# Set build arguments
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION=1.0.0

# Set metadata
LABEL maintainer="AutoSocioly Team <contact@autosocioly.com>" \
      org.opencontainers.image.title="AutoSocioly Social Media Automation" \
      org.opencontainers.image.description="AI-powered social media content generation and posting platform" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.revision="${VCS_REF}" \
      org.opencontainers.image.source="https://github.com/your-username/AutoSocioly" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.vendor="AutoSocioly" \
      org.opencontainers.image.url="https://autosocioly.com" \
      org.opencontainers.image.documentation="https://docs.autosocioly.com" \
      org.opencontainers.image.authors="AutoSocioly Development Team"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim as production

# Set build arguments
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION=1.0.0

# Set metadata (same as builder stage)
LABEL maintainer="AutoSocioly Team <contact@autosocioly.com>" \
      org.opencontainers.image.title="AutoSocioly Social Media Automation" \
      org.opencontainers.image.description="AI-powered social media content generation and posting platform" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.revision="${VCS_REF}" \
      org.opencontainers.image.source="https://github.com/your-username/AutoSocioly" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.vendor="AutoSocioly" \
      org.opencontainers.image.url="https://autosocioly.com" \
      org.opencontainers.image.documentation="https://docs.autosocioly.com" \
      org.opencontainers.image.authors="AutoSocioly Development Team"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PATH="/opt/venv/bin:$PATH" \
    APP_USER=autosocioly \
    APP_HOME=/app \
    REDIS_URL=redis://redis:6379/0

# Create non-root user
RUN groupadd -r ${APP_USER} && useradd -r -g ${APP_USER} -d ${APP_HOME} -s /bin/bash ${APP_USER}

# Install system dependencies for production
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create application directory
RUN mkdir -p ${APP_HOME}/static/uploads && \
    mkdir -p ${APP_HOME}/logs && \
    mkdir -p ${APP_HOME}/templates && \
    chown -R ${APP_USER}:${APP_USER} ${APP_HOME}

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Set working directory
WORKDIR ${APP_HOME}

# Copy application code
COPY --chown=${APP_USER}:${APP_USER} . .

# Create necessary directories and set permissions
RUN mkdir -p static/uploads logs && \
    chown -R ${APP_USER}:${APP_USER} static uploads logs

# Switch to non-root user
USER ${APP_USER}

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Default command
CMD ["python", "app.py"]

# Development stage
FROM production as development

# Switch back to root for development dependencies
USER root

# Install development dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install development Python packages
RUN pip install --no-cache-dir \
    pytest \
    pytest-cov \
    black \
    flake8 \
    mypy

# Switch back to app user
USER ${APP_USER}

# Development command with hot reload
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]