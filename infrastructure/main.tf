provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_bigquery_dataset" "mcp_playground" {
  dataset_id                  = "mcp_playground"
  friendly_name               = "MCP Playground"
  description                 = "Sandbox dataset for testing the Custom MCP Server"
  location                    = "US"
  default_table_expiration_ms = 3600000 # 1 hour expiration for safety
}

resource "google_bigquery_table" "dummy_customers" {
  dataset_id = google_bigquery_dataset.mcp_playground.dataset_id
  table_id   = "dummy_customers"

  schema = <<EOF
[
  {
    "name": "customer_id",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "Unique identifier for the customer"
  },
  {
    "name": "full_name",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "Customer's full name"
  },
  {
    "name": "email",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "Contact email"
  },
  {
    "name": "total_spend",
    "type": "FLOAT",
    "mode": "NULLABLE",
    "description": "Total amount spent by the customer"
  },
  {
    "name": "last_purchase_date",
    "type": "DATE",
    "mode": "NULLABLE",
    "description": "Date of last transaction"
  }
]
EOF
}
