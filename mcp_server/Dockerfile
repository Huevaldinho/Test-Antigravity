FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy server code
COPY server.py .

# Expose port (if using SSE, though stdio is default for local MCP)
# For Docker, we usually use SSE (Server-Sent Events) or stdio over a pipe.
# Since we are "distributing" this, let's assume we might want to expose it via HTTP/SSE later.
# But for now, the simplest way to run it is just keeping the process alive or running the script.
# We'll use the FastMCP run command.

CMD ["python", "server.py"]
