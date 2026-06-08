"""Run a single orchestrator mission via ADK Runner (no HTTP server)."""

from __future__ import annotations

import sys

from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.agent import root_agent

import sys as _sys

PROMPT = (
    "Show the codebase log timeline for github.com/demo/api-service. "
    "What file edits, decisions, and errors happened? "
    "Also query modex_logs synced via Fivetran and cite _fivetran_synced. "
    "What should a new Antigravity agent know?"
)
if len(_sys.argv) > 1:
    PROMPT = _sys.argv[1]


def main() -> int:
    session_service = InMemorySessionService()
    session = session_service.create_session_sync(
        user_id="hackathon_user",
        app_name="app",
    )
    runner = Runner(
        agent=root_agent,
        session_service=session_service,
        app_name="app",
    )
    message = types.Content(
        role="user",
        parts=[types.Part.from_text(text=PROMPT)],
    )
    print("Mission:", PROMPT)
    print("-" * 60)
    for event in runner.run(
        new_message=message,
        user_id="hackathon_user",
        session_id=session.id,
        run_config=RunConfig(streaming_mode=StreamingMode.SSE),
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(part.text)
    print("-" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
