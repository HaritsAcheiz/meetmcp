FROM python:3.12.9-slim-bookworm

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
WORKDIR /app
COPY ./client/ ./
COPY entrypoint.sh ./

# Make entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Install UV and add to PATH
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Init UV
RUN uv init

# Create virtual environment and install packages
RUN uv venv
RUN . ./.venv/bin/activate && \
    uv add "mcp[cli]==1.6.0" "nest-asyncio==1.6.0" "pillow==11.2.1" "streamlit==1.44.1"

# Create non-root user
RUN useradd -m mcpuser && \
    chown -R mcpuser:mcpuser /app

USER mcpuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["./entrypoint.sh"]