"""Runtime configuration for the Agentic Data Platform."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parents[1]
_HACKATHON_ROOT = _ROOT.parent

# Load agent project .env first, then hackathon root .env (Fivetran keys live there).
load_dotenv(_ROOT / ".env")
load_dotenv(_HACKATHON_ROOT / ".env")

GOOGLE_CLOUD_PROJECT = os.getenv(
    "GOOGLE_CLOUD_PROJECT", "gen-lang-client-0795401430"
)
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

FIVETRAN_API_KEY = os.getenv("FIVETRAN_API_KEY", "")
FIVETRAN_API_SECRET = os.getenv("FIVETRAN_API_SECRET", "")
FIVETRAN_ALLOW_WRITES = os.getenv("FIVETRAN_ALLOW_WRITES", "false").lower() == "true"
FIVETRAN_MCP_COMMAND = os.getenv("FIVETRAN_MCP_COMMAND", "uvx")
FIVETRAN_MCP_ARGS = os.getenv(
    "FIVETRAN_MCP_ARGS",
    "--from,git+https://github.com/fivetran/fivetran-mcp,fivetran-mcp",
)

# Live inventory from verified setup (2026-06-07).
FIVETRAN_BQ_GROUP_ID = os.getenv("FIVETRAN_BQ_GROUP_ID", "solve_unhurt")



# Fivetran Platform Connector metadata (pipeline observability + lineage).
BQ_METADATA_DATASET = os.getenv(
    "BQ_METADATA_DATASET", "fivetran_metadata_solve_unhurt"
)
BQ_METADATA_PREFIX = f"{GOOGLE_CLOUD_PROJECT}.{BQ_METADATA_DATASET}"

# Vertex AI RAG Engine (vector search) corpus for the Knowledge Agent.
RAG_CORPUS = os.getenv(
    "RAG_CORPUS",
    "projects/979112189932/locations/europe-west3/ragCorpora/4611686018427387904",
)
RAG_LOCATION = os.getenv("RAG_LOCATION", "europe-west3")
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "5"))

# Fivetran dbt Core transformation project (Transformation Agent).
FIVETRAN_TRANSFORM_PROJECT_ID = os.getenv(
    "FIVETRAN_TRANSFORM_PROJECT_ID", "gracious_electable"
)
FIVETRAN_TRANSFORMATION_ID = os.getenv("FIVETRAN_TRANSFORMATION_ID", "buy_tender")

# Action Agent — push insights to external targets (Guardian-gated writes).
ACTION_GCS_BUCKET = os.getenv(
    "ACTION_GCS_BUCKET",
    os.getenv(
        "LOGS_BUCKET_NAME",
        f"{GOOGLE_CLOUD_PROJECT}-action-reports",
    ),
)
ACTION_REPORT_SHEET_ID = os.getenv("ACTION_REPORT_SHEET_ID", "")
ACTION_SHEET_RANGE = os.getenv("ACTION_SHEET_RANGE", "Agent Reports!A1")
ACTION_WEBHOOK_URL = os.getenv("ACTION_WEBHOOK_URL", "")

# Face 1 — MoDeX developer-edge session memory (Cursor / Antigravity MCP).
MODEX_MEMORY_DATASET = os.getenv("MODEX_MEMORY_DATASET", "agent_memory")
MODEX_MEMORY_TABLE = os.getenv("MODEX_MEMORY_TABLE", "session_logs")
MODEX_CODEBASE_LOGS_TABLE = os.getenv("MODEX_CODEBASE_LOGS_TABLE", "codebase_logs")
MODEX_MEMORY_FULL_TABLE = (
    f"{GOOGLE_CLOUD_PROJECT}.{MODEX_MEMORY_DATASET}.{MODEX_MEMORY_TABLE}"
)
MODEX_CODEBASE_LOGS_FULL_TABLE = (
    f"{GOOGLE_CLOUD_PROJECT}.{MODEX_MEMORY_DATASET}.{MODEX_CODEBASE_LOGS_TABLE}"
)
MODEX_MEMORY_SHEET_ID = os.getenv(
    "MODEX_MEMORY_SHEET_ID", os.getenv("ACTION_REPORT_SHEET_ID", "")
)
MODEX_MEMORY_SHEET_RANGE = os.getenv("MODEX_MEMORY_SHEET_RANGE", "MoDeX Memory!A1")
MODEX_LOG_SHEET_RANGE = os.getenv("MODEX_LOG_SHEET_RANGE", "MoDex_Logs!A1")
FIVETRAN_MODEX_LOGS_CONNECTION_ID = os.getenv(
    "FIVETRAN_MODEX_LOGS_CONNECTION_ID", "stowed_register"
)
MODEX_FIVETRAN_BQ_DATASET = os.getenv("MODEX_FIVETRAN_BQ_DATASET", "modex_logs")
MODEX_FIVETRAN_BQ_TABLE = os.getenv("MODEX_FIVETRAN_BQ_TABLE", "modex_logs")
MODEX_FIVETRAN_FULL_TABLE = (
    f"{GOOGLE_CLOUD_PROJECT}.{MODEX_FIVETRAN_BQ_DATASET}.{MODEX_FIVETRAN_BQ_TABLE}"
)
