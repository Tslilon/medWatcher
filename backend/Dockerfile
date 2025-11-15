# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including Google Cloud SDK
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    gnupg \
    apt-transport-https \
    ca-certificates \
    tesseract-ocr \
    ffmpeg \
    libheif-dev \
    && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list \
    && apt-get update && apt-get install -y google-cloud-cli \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for data and static files
RUN mkdir -p /app/data /app/static

# Expose port (Cloud Run will set PORT env var)
ENV PORT=8080

# Create startup script that downloads data then starts the server
RUN echo '#!/bin/bash\n\
set -e\n\
echo "🚀 Starting Harrison Medical RAG..."\n\
python download_data.py\n\
echo "✅ Data ready, starting server..."\n\
exec uvicorn main:app --host 0.0.0.0 --port ${PORT}' > /app/start.sh \
    && chmod +x /app/start.sh

# Run the startup script
CMD ["/app/start.sh"]

