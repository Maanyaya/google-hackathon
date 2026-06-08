"""Delete a broken Agent Runtime reasoning engine (fresh deploy prerequisite)."""

from __future__ import annotations

import sys

from google.cloud import aiplatform_v1

ENGINE_ID = "4567336117409415168"
PROJECT_NUMBER = "979112189932"
REGION = "asia-south1"


def main() -> int:
    name = (
        f"projects/{PROJECT_NUMBER}/locations/{REGION}/"
        f"reasoningEngines/{ENGINE_ID}"
    )
    api = aiplatform_v1.ReasoningEngineServiceClient(
        client_options={"api_endpoint": f"{REGION}-aiplatform.googleapis.com"}
    )
    print(f"Deleting {name} ...")
    api.delete_reasoning_engine(
        request=aiplatform_v1.DeleteReasoningEngineRequest(name=name, force=True)
    )
    print("Delete requested. Wait ~2 min before redeploying.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
