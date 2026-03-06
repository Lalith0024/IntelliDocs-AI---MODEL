# Use an official lightweight Python image.
# heavily optimized for minimal size
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Optimize for low memory environments (Render Free Tier)
ENV OMP_NUM_THREADS=1
ENV MKL_NUM_THREADS=1
ENV FASTEMBED_CACHE_PATH=/app/cache
ENV HF_HOME=/app/cache
ENV TMPDIR=/tmp

# Copy requirements file first for layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the entire backend codebase
# .dockerignore ensures we don't copy the frontend or venv
COPY . .

# Pre-download the FastEmbed model during build
# Using a small, high-quality model: BAAI/bge-small-en-v1.5
RUN python -c "from fastembed import TextEmbedding; TextEmbedding(model_name='BAAI/bge-small-en-v1.5')"

# Expose the port (Render default is 10000)
EXPOSE 10000

# Run the application with uvicorn
# Use 1 worker to save memory
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000", "--workers", "1"]
