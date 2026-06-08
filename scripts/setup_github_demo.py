"""Seed a Fivetran-faithful GitHub dataset (github_demo) for MoDeX.

This mirrors the schema the Fivetran GitHub connector lands in BigQuery
(`pull_request`, `pull_request_review`, `repository`, `user`, all with
`_fivetran_synced`). The seed rows correspond to the engineering decisions
already in `agent_memory.codebase_logs`, so MoDeX can cross-reference a
coding-agent's session decision against the real PR + reviewer reasoning.

When your live Fivetran GitHub connector finishes its first sync into a
`github` dataset, just set GITHUB_DATASET=github and everything works unchanged.

Run:  uv run python scripts/setup_github_demo.py
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from google.cloud import bigquery

from app import config

_NOW = datetime.now(timezone.utc)


def _iso(days_ago: float) -> str:
    return (_NOW - timedelta(days=days_ago)).isoformat()


def _synced(minutes_ago: float) -> str:
    return (_NOW - timedelta(minutes=minutes_ago)).isoformat()


REPOSITORY = [
    {
        "id": 1,
        "full_name": config.GITHUB_REPO_FULL_NAME,
        "name": config.GITHUB_REPO_FULL_NAME.split("/")[-1],
        "private": True,
        "html_url": f"https://github.com/{config.GITHUB_REPO_FULL_NAME}",
        "created_at": _iso(180),
        "_fivetran_synced": _synced(4),
        "_fivetran_deleted": False,
    }
]

USERS = [
    {"id": 101, "login": "alice", "name": "Alice Chen", "type": "User", "_fivetran_synced": _synced(4), "_fivetran_deleted": False},
    {"id": 102, "login": "bob", "name": "Bob Ortiz", "type": "User", "_fivetran_synced": _synced(4), "_fivetran_deleted": False},
    {"id": 103, "login": "carol", "name": "Carol Nadu", "type": "User", "_fivetran_synced": _synced(4), "_fivetran_deleted": False},
]

PULL_REQUESTS = [
    {
        "id": 9142, "number": 142, "repository_id": 1,
        "title": "Migrate auth store to PostgreSQL",
        "body": ("Switch the auth/session store from MongoDB to PostgreSQL. "
                 "We need ACID transactions for credential rotation and token "
                 "revocation; Mongo's lack of multi-document transactions bit us. "
                 "Rationale: transactional integrity > flexible schema here."),
        "state": "closed", "user_id": 102,
        "created_at": _iso(19), "updated_at": _iso(17), "closed_at": _iso(17),
        "merged_at": _iso(17), "merged": True,
        "merge_commit_sha": "a1b2c3d4e5f6", "base_ref": "main", "head_ref": "auth-postgres",
        "html_url": f"https://github.com/{config.GITHUB_REPO_FULL_NAME}/pull/142",
        "_fivetran_synced": _synced(4), "_fivetran_deleted": False,
    },
    {
        "id": 9088, "number": 88, "repository_id": 1,
        "title": "Spike: MongoDB for session store",
        "body": ("Prototype using MongoDB as the primary session/credential store "
                 "for flexibility. Open question: can we live without multi-document "
                 "transactions?"),
        "state": "closed", "user_id": 103,
        "created_at": _iso(26), "updated_at": _iso(24), "closed_at": _iso(24),
        "merged_at": None, "merged": False,
        "merge_commit_sha": None, "base_ref": "main", "head_ref": "spike-mongo",
        "html_url": f"https://github.com/{config.GITHUB_REPO_FULL_NAME}/pull/88",
        "_fivetran_synced": _synced(4), "_fivetran_deleted": False,
    },
    {
        "id": 9150, "number": 150, "repository_id": 1,
        "title": "Adopt JWT for auth tokens",
        "body": ("Replace server-side session cookies with stateless JWT access "
                 "tokens + refresh tokens. Rationale: stateless verification scales "
                 "horizontally without sticky sessions or a shared session cache."),
        "state": "closed", "user_id": 101,
        "created_at": _iso(12), "updated_at": _iso(11), "closed_at": _iso(11),
        "merged_at": _iso(11), "merged": True,
        "merge_commit_sha": "f6e5d4c3b2a1", "base_ref": "main", "head_ref": "jwt-auth",
        "html_url": f"https://github.com/{config.GITHUB_REPO_FULL_NAME}/pull/150",
        "_fivetran_synced": _synced(4), "_fivetran_deleted": False,
    },
    {
        "id": 9161, "number": 161, "repository_id": 1,
        "title": "Add idempotency keys to payment webhook",
        "body": ("Payment webhook was double-processing on retries. Add idempotency "
                 "keys stored in Postgres with a unique constraint so replays are no-ops."),
        "state": "open", "user_id": 102,
        "created_at": _iso(3), "updated_at": _iso(1), "closed_at": None,
        "merged_at": None, "merged": False,
        "merge_commit_sha": None, "base_ref": "main", "head_ref": "idempotent-webhook",
        "html_url": f"https://github.com/{config.GITHUB_REPO_FULL_NAME}/pull/161",
        "_fivetran_synced": _synced(4), "_fivetran_deleted": False,
    },
]

PULL_REQUEST_REVIEWS = [
    {
        "id": 70142, "pull_request_id": 9142, "user_id": 101, "state": "APPROVED",
        "body": ("Agreed. Transactional integrity for credential rotation is "
                 "non-negotiable. Postgres is the right call."),
        "submitted_at": _iso(17), "commit_id": "a1b2c3d4e5f6",
        "_fivetran_synced": _synced(4), "_fivetran_deleted": False,
    },
    {
        "id": 70088, "pull_request_id": 9088, "user_id": 102, "state": "CHANGES_REQUESTED",
        "body": ("Rejecting this direction. No multi-document transactions means we "
                 "can't guarantee atomic credential updates. Go with PostgreSQL instead."),
        "submitted_at": _iso(24), "commit_id": None,
        "_fivetran_synced": _synced(4), "_fivetran_deleted": False,
    },
    {
        "id": 70150, "pull_request_id": 9150, "user_id": 103, "state": "APPROVED",
        "body": ("Stateless JWT scales better than session cookies for our multi-region "
                 "deployment. Make sure refresh-token rotation is solid."),
        "submitted_at": _iso(11), "commit_id": "f6e5d4c3b2a1",
        "_fivetran_synced": _synced(4), "_fivetran_deleted": False,
    },
]


_SCHEMAS: dict[str, list[bigquery.SchemaField]] = {
    "repository": [
        bigquery.SchemaField("id", "INTEGER"),
        bigquery.SchemaField("full_name", "STRING"),
        bigquery.SchemaField("name", "STRING"),
        bigquery.SchemaField("private", "BOOLEAN"),
        bigquery.SchemaField("html_url", "STRING"),
        bigquery.SchemaField("created_at", "TIMESTAMP"),
        bigquery.SchemaField("_fivetran_synced", "TIMESTAMP"),
        bigquery.SchemaField("_fivetran_deleted", "BOOLEAN"),
    ],
    "user": [
        bigquery.SchemaField("id", "INTEGER"),
        bigquery.SchemaField("login", "STRING"),
        bigquery.SchemaField("name", "STRING"),
        bigquery.SchemaField("type", "STRING"),
        bigquery.SchemaField("_fivetran_synced", "TIMESTAMP"),
        bigquery.SchemaField("_fivetran_deleted", "BOOLEAN"),
    ],
    "pull_request": [
        bigquery.SchemaField("id", "INTEGER"),
        bigquery.SchemaField("number", "INTEGER"),
        bigquery.SchemaField("repository_id", "INTEGER"),
        bigquery.SchemaField("title", "STRING"),
        bigquery.SchemaField("body", "STRING"),
        bigquery.SchemaField("state", "STRING"),
        bigquery.SchemaField("user_id", "INTEGER"),
        bigquery.SchemaField("created_at", "TIMESTAMP"),
        bigquery.SchemaField("updated_at", "TIMESTAMP"),
        bigquery.SchemaField("closed_at", "TIMESTAMP"),
        bigquery.SchemaField("merged_at", "TIMESTAMP"),
        bigquery.SchemaField("merged", "BOOLEAN"),
        bigquery.SchemaField("merge_commit_sha", "STRING"),
        bigquery.SchemaField("base_ref", "STRING"),
        bigquery.SchemaField("head_ref", "STRING"),
        bigquery.SchemaField("html_url", "STRING"),
        bigquery.SchemaField("_fivetran_synced", "TIMESTAMP"),
        bigquery.SchemaField("_fivetran_deleted", "BOOLEAN"),
    ],
    "pull_request_review": [
        bigquery.SchemaField("id", "INTEGER"),
        bigquery.SchemaField("pull_request_id", "INTEGER"),
        bigquery.SchemaField("user_id", "INTEGER"),
        bigquery.SchemaField("state", "STRING"),
        bigquery.SchemaField("body", "STRING"),
        bigquery.SchemaField("submitted_at", "TIMESTAMP"),
        bigquery.SchemaField("commit_id", "STRING"),
        bigquery.SchemaField("_fivetran_synced", "TIMESTAMP"),
        bigquery.SchemaField("_fivetran_deleted", "BOOLEAN"),
    ],
}

_ROWS: dict[str, list[dict]] = {
    "repository": REPOSITORY,
    "user": USERS,
    "pull_request": PULL_REQUESTS,
    "pull_request_review": PULL_REQUEST_REVIEWS,
}


def main() -> None:
    client = bigquery.Client(project=config.GOOGLE_CLOUD_PROJECT)
    dataset_id = f"{config.GOOGLE_CLOUD_PROJECT}.{config.GITHUB_DATASET}"

    ds = bigquery.Dataset(dataset_id)
    ds.location = "US"
    client.create_dataset(ds, exists_ok=True)
    print(f"dataset ready: {dataset_id}")

    for table_name, schema in _SCHEMAS.items():
        table_id = f"{dataset_id}.{table_name}"
        job_config = bigquery.LoadJobConfig(
            schema=schema,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        )
        job = client.load_table_from_json(
            _ROWS[table_name], table_id, job_config=job_config
        )
        job.result()
        print(f"  loaded {len(_ROWS[table_name])} rows -> {table_name}")

    print("\ngithub_demo seed complete. Tables mirror the Fivetran GitHub schema.")


if __name__ == "__main__":
    main()
