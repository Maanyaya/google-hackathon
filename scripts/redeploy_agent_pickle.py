"""Redeploy Agent Runtime using pickle package_spec (fixes Playground instance error)."""

from __future__ import annotations

import os
import sys
import time

import vertexai
from google.cloud import aiplatform_v1
from vertexai import agent_engines

from app.agent_runtime_app import agent_runtime

PROJECT = "gen-lang-client-0795401430"
PROJECT_NUMBER = "979112189932"
REGION = "asia-south1"
DISPLAY_NAME = "agentic-data-platform"
STAGING_BUCKET = "gs://gen-lang-client-0795401430-agentic-data-platform-logs"
ENGINE_TO_DELETE = "3807353680290643968"

ENV_VARS = {
    "GOOGLE_GENAI_USE_VERTEXAI": "True",
    "GOOGLE_CLOUD_LOCATION": "global",
    "FIVETRAN_ALLOW_WRITES": "false",
    "BQ_METADATA_DATASET": "fivetran_metadata_solve_unhurt",
    "RAG_CORPUS": "projects/979112189932/locations/europe-west3/ragCorpora/4611686018427387904",
    "RAG_LOCATION": "europe-west3",
    "FIVETRAN_TRANSFORM_PROJECT_ID": "gracious_electable",
    "FIVETRAN_TRANSFORMATION_ID": "buy_tender",
    "FIVETRAN_MODEX_LOGS_CONNECTION_ID": "stowed_register",
    "MODEX_FIVETRAN_BQ_DATASET": "modex_logs",
    "MODEX_FIVETRAN_BQ_TABLE": "modex_logs",
    "LOGS_BUCKET_NAME": "gen-lang-client-0795401430-agentic-data-platform-logs",
    "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": "NO_CONTENT",
}


def _delete_engine(engine_id: str) -> None:
    api = aiplatform_v1.ReasoningEngineServiceClient(
        client_options={"api_endpoint": f"{REGION}-aiplatform.googleapis.com"}
    )
    name = (
        f"projects/{PROJECT_NUMBER}/locations/{REGION}/reasoningEngines/{engine_id}"
    )
    try:
        api.delete_reasoning_engine(
            request=aiplatform_v1.DeleteReasoningEngineRequest(name=name, force=True)
        )
        print(f"Deleted {engine_id}, waiting 90s...")
        time.sleep(90)
    except Exception as exc:  # noqa: BLE001
        print(f"Delete skipped/failed: {exc}")


def main() -> int:
    _delete_engine(ENGINE_TO_DELETE)

    vertexai.init(project=PROJECT, location=REGION, staging_bucket=STAGING_BUCKET)
    print("Creating engine with pickle package_spec...")
    remote = agent_engines.create(
        agent_engine=agent_runtime,
        requirements="app/app_utils/.requirements.txt",
        extra_packages=["./app"],
        display_name=DISPLAY_NAME,
        env_vars=ENV_VARS,
        min_instances=1,
        max_instances=10,
        resource_limits={"cpu": "4", "memory": "8Gi"},
        container_concurrency=9,
    )
    print("SUCCESS")
    print(remote.resource_name)
    print(
        "Playground:",
        f"https://console.cloud.google.com/vertex-ai/agents/agent-engines/locations/{REGION}/agent-engines/{remote.resource_name.split('/')[-1]}/playground?project={PROJECT}",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
