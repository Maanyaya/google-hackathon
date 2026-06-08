"""Seed Fivetran-faithful Jira (jira_demo) + Slack (slack_demo) datasets for MoDeX.

These mirror the schemas the Fivetran Jira and Slack connectors land in BigQuery
(`issue`, `comment`, `project`, `user` for Jira; `channel`, `message`, `user` for
Slack — all with `_fivetran_synced` / `_fivetran_deleted`).

The rows corroborate the SAME engineering decisions already present in
`agent_memory.codebase_logs` and `github_demo` (PostgreSQL-over-MongoDB, JWT vs
session cookies, payment-webhook idempotency). That lets MoDeX cross-reference a
single decision across FOUR independent sources: the coding-agent session, the
GitHub PR review, the Jira ticket, and the Slack thread.

When your live Fivetran Jira/Slack connectors finish their first sync, just set
JIRA_DATASET=jira / SLACK_DATASET=slack and everything works unchanged.

Run:  uv run python scripts/setup_jira_slack_demo.py
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


def _ts(days_ago: float, seq: int) -> str:
    """Slack-style message id: '<epoch>.<6-digit seq>'."""
    epoch = (_NOW - timedelta(days=days_ago)).timestamp()
    return f"{epoch:.0f}.{seq:06d}"


# --------------------------------------------------------------------------- #
# Jira (jira_demo) — planning-level "why"
# --------------------------------------------------------------------------- #
JIRA_PROJECT = [
    {"id": 1, "key": "PLAT", "name": "Payments Platform",
     "_fivetran_synced": _synced(6), "_fivetran_deleted": False},
]

JIRA_USERS = [
    {"id": "acct-alice", "account_id": "acct-alice", "display_name": "Alice Chen",
     "email_address": "alice@demo.dev", "active": True,
     "_fivetran_synced": _synced(6), "_fivetran_deleted": False},
    {"id": "acct-bob", "account_id": "acct-bob", "display_name": "Bob Ortiz",
     "email_address": "bob@demo.dev", "active": True,
     "_fivetran_synced": _synced(6), "_fivetran_deleted": False},
    {"id": "acct-carol", "account_id": "acct-carol", "display_name": "Carol Nadu",
     "email_address": "carol@demo.dev", "active": True,
     "_fivetran_synced": _synced(6), "_fivetran_deleted": False},
]

JIRA_ISSUES = [
    {
        "id": 5142, "key": "PLAT-142", "project_id": 1,
        "summary": "Select primary datastore for the auth and session store",
        "description": ("Evaluate MongoDB vs PostgreSQL for the authentication and "
                        "session/credential store. Must guarantee transactional "
                        "consistency (ACID) for credential rotation and token "
                        "revocation. MongoDB lacks multi-document transactions."),
        "status": "Done", "issue_type": "Story", "priority": "High",
        "assignee_id": "acct-bob", "reporter_id": "acct-alice",
        "created": _iso(22), "updated": _iso(17), "resolved": _iso(17),
        "_fivetran_synced": _synced(6), "_fivetran_deleted": False,
    },
    {
        "id": 5150, "key": "PLAT-150", "project_id": 1,
        "summary": "Auth token strategy - replace session cookies with stateless JWT",
        "description": ("Move from server-side session cookies to stateless JWT "
                        "access tokens plus refresh tokens, so verification scales "
                        "horizontally for multi-region without sticky sessions."),
        "status": "Done", "issue_type": "Story", "priority": "Medium",
        "assignee_id": "acct-alice", "reporter_id": "acct-carol",
        "created": _iso(14), "updated": _iso(11), "resolved": _iso(11),
        "_fivetran_synced": _synced(6), "_fivetran_deleted": False,
    },
    {
        "id": 5168, "key": "PLAT-168", "project_id": 1,
        "summary": "Payment webhook double-processes on retry",
        "description": ("Payment webhook double-processes events on retries. Add "
                        "idempotency keys persisted in PostgreSQL with a unique "
                        "constraint so replays are no-ops."),
        "status": "In Progress", "issue_type": "Bug", "priority": "High",
        "assignee_id": "acct-bob", "reporter_id": "acct-bob",
        "created": _iso(3), "updated": _iso(1), "resolved": None,
        "_fivetran_synced": _synced(6), "_fivetran_deleted": False,
    },
]

JIRA_COMMENTS = [
    {"id": 81421, "issue_id": 5142, "author_id": "acct-bob",
     "body": ("Spike confirmed MongoDB can't do multi-document transactions for "
              "credential rotation. Decision: PostgreSQL."),
     "created": _iso(18), "updated": _iso(18),
     "_fivetran_synced": _synced(6), "_fivetran_deleted": False},
    {"id": 81422, "issue_id": 5142, "author_id": "acct-alice",
     "body": ("Agreed - PostgreSQL for ACID / transactional consistency. Closing "
              "the Mongo spike."),
     "created": _iso(17), "updated": _iso(17),
     "_fivetran_synced": _synced(6), "_fivetran_deleted": False},
    {"id": 81501, "issue_id": 5150, "author_id": "acct-carol",
     "body": ("Stateless JWT scales for multi-region; drop the session cookies. "
              "Ship it - just make refresh-token rotation solid."),
     "created": _iso(11), "updated": _iso(11),
     "_fivetran_synced": _synced(6), "_fivetran_deleted": False},
    {"id": 81681, "issue_id": 5168, "author_id": "acct-bob",
     "body": "Implementing idempotency keys with a unique constraint in Postgres.",
     "created": _iso(1), "updated": _iso(1),
     "_fivetran_synced": _synced(6), "_fivetran_deleted": False},
]


# --------------------------------------------------------------------------- #
# Slack (slack_demo) — where the decision was actually debated
# --------------------------------------------------------------------------- #
SLACK_CHANNELS = [
    {"id": "C100", "name": "eng-data", "topic": "Data & storage decisions",
     "is_private": False, "created": _iso(120),
     "_fivetran_synced": _synced(3), "_fivetran_deleted": False},
    {"id": "C300", "name": "architecture", "topic": "Architecture & RFCs",
     "is_private": False, "created": _iso(120),
     "_fivetran_synced": _synced(3), "_fivetran_deleted": False},
    {"id": "C200", "name": "incidents", "topic": "Production incidents",
     "is_private": False, "created": _iso(120),
     "_fivetran_synced": _synced(3), "_fivetran_deleted": False},
]

SLACK_USERS = [
    {"id": "U101", "name": "alice", "real_name": "Alice Chen", "is_bot": False,
     "_fivetran_synced": _synced(3), "_fivetran_deleted": False},
    {"id": "U102", "name": "bob", "real_name": "Bob Ortiz", "is_bot": False,
     "_fivetran_synced": _synced(3), "_fivetran_deleted": False},
    {"id": "U103", "name": "carol", "real_name": "Carol Nadu", "is_bot": False,
     "_fivetran_synced": _synced(3), "_fivetran_deleted": False},
]

_T1 = _ts(18, 100)   # postgres vs mongo thread root (eng-data)
_T2 = _ts(12, 200)   # jwt vs cookies thread root (architecture)
_T3 = _ts(2, 300)    # idempotency thread root (incidents)

SLACK_MESSAGES = [
    # Thread 1 - PostgreSQL over MongoDB
    {"ts": _T1, "channel_id": "C100", "user_id": "U102",
     "text": ("the mongodb spike for the credential/session store keeps biting us "
              "- no multi-document transactions"),
     "thread_ts": _T1, "reply_count": 2,
     "_fivetran_synced": _synced(3), "_fivetran_deleted": False},
    {"ts": _ts(18, 101), "channel_id": "C100", "user_id": "U101",
     "text": ("right, we need transactional consistency for credential rotation. "
              "moving to postgresql"),
     "thread_ts": _T1, "reply_count": 0,
     "_fivetran_synced": _synced(3), "_fivetran_deleted": False},
    {"ts": _ts(18, 102), "channel_id": "C100", "user_id": "U103",
     "text": ("+1 postgresql. flexible schema isn't worth losing ACID / "
              "transactional integrity here"),
     "thread_ts": _T1, "reply_count": 0,
     "_fivetran_synced": _synced(3), "_fivetran_deleted": False},
    # Thread 2 - JWT over session cookies
    {"ts": _T2, "channel_id": "C300", "user_id": "U101",
     "text": ("proposal: drop server-side session cookies, go stateless jwt "
              "access + refresh tokens"),
     "thread_ts": _T2, "reply_count": 1,
     "_fivetran_synced": _synced(3), "_fivetran_deleted": False},
    {"ts": _ts(12, 201), "channel_id": "C300", "user_id": "U103",
     "text": ("stateless jwt verification scales horizontally for multi-region, "
              "no sticky sessions. +1, replace the cookies"),
     "thread_ts": _T2, "reply_count": 0,
     "_fivetran_synced": _synced(3), "_fivetran_deleted": False},
    # Thread 3 - payment webhook idempotency
    {"ts": _T3, "channel_id": "C200", "user_id": "U102",
     "text": "payment webhook is double-processing on retries again",
     "thread_ts": _T3, "reply_count": 1,
     "_fivetran_synced": _synced(3), "_fivetran_deleted": False},
    {"ts": _ts(2, 301), "channel_id": "C200", "user_id": "U101",
     "text": ("add idempotency keys in postgresql with a unique constraint so "
              "replays are no-ops"),
     "thread_ts": _T3, "reply_count": 0,
     "_fivetran_synced": _synced(3), "_fivetran_deleted": False},
]


_JIRA_SCHEMAS: dict[str, list[bigquery.SchemaField]] = {
    "project": [
        bigquery.SchemaField("id", "INTEGER"),
        bigquery.SchemaField("key", "STRING"),
        bigquery.SchemaField("name", "STRING"),
        bigquery.SchemaField("_fivetran_synced", "TIMESTAMP"),
        bigquery.SchemaField("_fivetran_deleted", "BOOLEAN"),
    ],
    "user": [
        bigquery.SchemaField("id", "STRING"),
        bigquery.SchemaField("account_id", "STRING"),
        bigquery.SchemaField("display_name", "STRING"),
        bigquery.SchemaField("email_address", "STRING"),
        bigquery.SchemaField("active", "BOOLEAN"),
        bigquery.SchemaField("_fivetran_synced", "TIMESTAMP"),
        bigquery.SchemaField("_fivetran_deleted", "BOOLEAN"),
    ],
    "issue": [
        bigquery.SchemaField("id", "INTEGER"),
        bigquery.SchemaField("key", "STRING"),
        bigquery.SchemaField("project_id", "INTEGER"),
        bigquery.SchemaField("summary", "STRING"),
        bigquery.SchemaField("description", "STRING"),
        bigquery.SchemaField("status", "STRING"),
        bigquery.SchemaField("issue_type", "STRING"),
        bigquery.SchemaField("priority", "STRING"),
        bigquery.SchemaField("assignee_id", "STRING"),
        bigquery.SchemaField("reporter_id", "STRING"),
        bigquery.SchemaField("created", "TIMESTAMP"),
        bigquery.SchemaField("updated", "TIMESTAMP"),
        bigquery.SchemaField("resolved", "TIMESTAMP"),
        bigquery.SchemaField("_fivetran_synced", "TIMESTAMP"),
        bigquery.SchemaField("_fivetran_deleted", "BOOLEAN"),
    ],
    "comment": [
        bigquery.SchemaField("id", "INTEGER"),
        bigquery.SchemaField("issue_id", "INTEGER"),
        bigquery.SchemaField("author_id", "STRING"),
        bigquery.SchemaField("body", "STRING"),
        bigquery.SchemaField("created", "TIMESTAMP"),
        bigquery.SchemaField("updated", "TIMESTAMP"),
        bigquery.SchemaField("_fivetran_synced", "TIMESTAMP"),
        bigquery.SchemaField("_fivetran_deleted", "BOOLEAN"),
    ],
}

_SLACK_SCHEMAS: dict[str, list[bigquery.SchemaField]] = {
    "channel": [
        bigquery.SchemaField("id", "STRING"),
        bigquery.SchemaField("name", "STRING"),
        bigquery.SchemaField("topic", "STRING"),
        bigquery.SchemaField("is_private", "BOOLEAN"),
        bigquery.SchemaField("created", "TIMESTAMP"),
        bigquery.SchemaField("_fivetran_synced", "TIMESTAMP"),
        bigquery.SchemaField("_fivetran_deleted", "BOOLEAN"),
    ],
    "user": [
        bigquery.SchemaField("id", "STRING"),
        bigquery.SchemaField("name", "STRING"),
        bigquery.SchemaField("real_name", "STRING"),
        bigquery.SchemaField("is_bot", "BOOLEAN"),
        bigquery.SchemaField("_fivetran_synced", "TIMESTAMP"),
        bigquery.SchemaField("_fivetran_deleted", "BOOLEAN"),
    ],
    "message": [
        bigquery.SchemaField("ts", "STRING"),
        bigquery.SchemaField("channel_id", "STRING"),
        bigquery.SchemaField("user_id", "STRING"),
        bigquery.SchemaField("text", "STRING"),
        bigquery.SchemaField("thread_ts", "STRING"),
        bigquery.SchemaField("reply_count", "INTEGER"),
        bigquery.SchemaField("_fivetran_synced", "TIMESTAMP"),
        bigquery.SchemaField("_fivetran_deleted", "BOOLEAN"),
    ],
}

_JIRA_ROWS = {
    "project": JIRA_PROJECT,
    "user": JIRA_USERS,
    "issue": JIRA_ISSUES,
    "comment": JIRA_COMMENTS,
}

_SLACK_ROWS = {
    "channel": SLACK_CHANNELS,
    "user": SLACK_USERS,
    "message": SLACK_MESSAGES,
}


def _seed(client: bigquery.Client, dataset: str, schemas: dict, rows: dict) -> None:
    dataset_id = f"{config.GOOGLE_CLOUD_PROJECT}.{dataset}"
    ds = bigquery.Dataset(dataset_id)
    ds.location = "US"
    client.create_dataset(ds, exists_ok=True)
    print(f"dataset ready: {dataset_id}")
    for table_name, schema in schemas.items():
        table_id = f"{dataset_id}.{table_name}"
        job_config = bigquery.LoadJobConfig(
            schema=schema,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        )
        job = client.load_table_from_json(rows[table_name], table_id, job_config=job_config)
        job.result()
        print(f"  loaded {len(rows[table_name])} rows -> {table_name}")


def main() -> None:
    client = bigquery.Client(project=config.GOOGLE_CLOUD_PROJECT)
    _seed(client, config.JIRA_DATASET, _JIRA_SCHEMAS, _JIRA_ROWS)
    _seed(client, config.SLACK_DATASET, _SLACK_SCHEMAS, _SLACK_ROWS)
    print("\njira_demo + slack_demo seed complete. Tables mirror the Fivetran "
          "Jira/Slack connector schemas and corroborate the same decisions as "
          "github_demo + the coding-agent session logs.")


if __name__ == "__main__":
    main()
