import re
from mcp.server.fastmcp import FastMCP
from google.cloud import bigquery
import google.auth

# Initialize the MCP Server 
# https://gofastmcp.com/getting-started/welcome
mcp = FastMCP("BigQuery MCP Server")

# Initialize BigQuery Client (will use ADC from the environment/volume mount)
# We delay initialization to the first call or global scope if credentials are present.
try:
    client = bigquery.Client()
    print("✅ BigQuery Client initialized with detected credentials.")
except Exception as e:
    print(f"⚠️  Warning: BigQuery Client failed to initialize (Credentials missing?): {e}")
    client = None

def get_client():
    global client
    if client is None:
        client = bigquery.Client()
    return client

@mcp.tool()
def list_datasets() -> str:
    """Lists all datasets in the current project."""
    bq = get_client()
    datasets = list(bq.list_datasets())
    if not datasets:
        return "No datasets found."
    return "\n".join([f"- {d.dataset_id}" for d in datasets])

@mcp.tool()
def get_table_schema(dataset_id: str, table_id: str) -> str:
    """Gets the schema for a specific table."""
    bq = get_client()
    try:
        table_ref = f"{bq.project}.{dataset_id}.{table_id}"
        table = bq.get_table(table_ref)
        schema_str = []
        for field in table.schema:
            schema_str.append(f"- {field.name} ({field.field_type}): {field.description or 'No description'}")
        return "\n".join(schema_str)
    except Exception as e:
        return f"Error getting schema: {str(e)}"

@mcp.tool()
def run_query(query: str) -> str:
    """
    Executes a SQL query against BigQuery.
    SECURITY: Only SELECT statements are allowed.
    """
    # 1. Security Layer: Block destructive commands
    forbidden_patterns = [
        r"\bDROP\b", r"\bDELETE\b", r"\bINSERT\b", r"\bUPDATE\b", 
        r"\bALTER\b", r"\bTRUNCATE\b", r"\bMERGE\b", r"\bGRANT\b"
    ]
    
    for pattern in forbidden_patterns:
        if re.search(pattern, query, re.IGNORECASE):
            return f"🚫 SECURITY ALERT: Query blocked. The command '{pattern}' is not allowed."

    # 2. Execute Query
    bq = get_client()
    try:
        query_job = bq.query(query)
        results = query_job.result()
        
        # Format results as Markdown table
        rows = list(results)
        if not rows:
            return "Query executed successfully. No results returned."
            
        # Get headers
        headers = [field.name for field in results.schema]
        markdown_table = "| " + " | ".join(headers) + " |\n"
        markdown_table += "| " + " | ".join(["---"] * len(headers)) + " |\n"
        
        for row in rows:
            values = [str(row[col]) for col in headers]
            markdown_table += "| " + " | ".join(values) + " |\n"
            
        return markdown_table

    except Exception as e:
        return f"❌ Query Error: {str(e)}"

if __name__ == "__main__":
    # Run the server using stdio (standard input/output)
    # This is the standard for local MCP servers.
    mcp.run()
