# Use a specific Python version — never use latest
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies first (cached layer)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies (cached if requirements.txt unchanged)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create a non-root user for security
RUN useradd -m -u 1000 agent && chown -R agent:agent /app
USER agent

# Health check endpoint — more on this in Step 4
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the agent
CMD ["python", "agent.py"]