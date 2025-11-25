# BigQuery MCP Server (Dockerized)

A custom Model Context Protocol (MCP) server for BigQuery, designed for enterprise environments.

## Features
- **Dockerized**: Fully containerized for easy distribution.
- **Secure**: Uses Application Default Credentials (ADC) and enforces read-only SQL policies.
- **MCP Compliant**: Implements `list_datasets`, `get_table_schema`, and `run_query`.

## Quick Start

### 1. Infrastructure
Provision the sandbox environment:
```bash
cd infrastructure
terraform init
terraform apply -var="project_id=YOUR_PROJECT_ID"
```

### 2. Run Server
```bash
# Set Project ID
$env:GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"

# Start Docker Container
docker-compose up --build -d
```

### 3. Run Client
```bash
# Install Client Deps
pip install -r mcp_client/requirements.txt

# Run Client
python mcp_client/client.py
```

## Structure
- `/infrastructure`: Terraform configuration.
- `/mcp_server`: The MCP server (Python + Dockerfile).
- `/mcp_client`: A Python client to test the server with Gemini.
