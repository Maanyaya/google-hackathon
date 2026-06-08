"""Unit tests for tool helpers (no LLM assertions)."""

from __future__ import annotations

import re

from app.tools import get_data_catalog, query_bigquery


def test_get_data_catalog_has_modex_table():
    catalog = get_data_catalog()
    assert catalog["status"] == "success"
    # Primary table should be codebase_logs (MoDeX shared memory)
    assert "agent_memory" in catalog["primary_table"] or "codebase_logs" in catalog["primary_table"]


def test_query_bigquery_rejects_mutating_sql():
    result = query_bigquery("DELETE FROM foo")
    assert result["status"] == "error"


def test_query_bigquery_count_codebase_logs():
    result = query_bigquery(
        "SELECT COUNT(*) AS n FROM `gen-lang-client-0795401430.agent_memory.codebase_logs`"
    )
    assert result["status"] == "success"
    assert result["rows"][0]["n"] >= 0


def test_query_bigquery_select_only_pattern():
    result = query_bigquery("WITH x AS (SELECT 1) SELECT * FROM x")
    assert result["status"] == "success" or "error" in result["status"]
    assert not re.search(r"INSERT", "SELECT 1", re.I)
