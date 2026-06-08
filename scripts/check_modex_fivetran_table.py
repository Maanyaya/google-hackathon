"""Verify Fivetran connector stowed_register landed data in BQ."""

from __future__ import annotations

from google.cloud import bigquery

PROJECT = "gen-lang-client-0795401430"
TABLE = f"{PROJECT}.modex_logs.modex_logs"


def main() -> None:
    client = bigquery.Client(project=PROJECT)
    try:
        rows = list(client.query(f"SELECT COUNT(*) AS n FROM `{TABLE}`").result())
        print(f"Table: {TABLE}")
        print(f"Row count: {rows[0].n}")
        sample = list(
            client.query(f"SELECT * FROM `{TABLE}` ORDER BY 1 DESC LIMIT 3").result()
        )
        for r in sample:
            print(dict(r.items()))
    except Exception as exc:  # noqa: BLE001
        print(f"Error querying {TABLE}: {exc}")


if __name__ == "__main__":
    main()
