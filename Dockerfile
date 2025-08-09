FROM python:3.11-slim

WORKDIR /app

# Install Node.js for MCP server
RUN apt-get update && \
    apt-get install -y nodejs npm curl && \
    npm install -g @aywengo/kafka-schema-reg-mcp && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p logs docs/schemas

# Environment variables
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]