"""Quick test: verify MoDeX dashboard API data endpoints."""

from __future__ import annotations

import json

from app import config
from app.dashboard_api import _run_bq, get_memory_timeline, get_overview


async def main() -> None:
    print("=== Overview ===")
    print(json.dumps(await get_overview(), indent=2))

    print("\n=== Freshness (Fivetran modex_logs) ===")
    r = _run_bq(
        f"SELECT MAX(_fivetran_synced) AS last_synced, COUNT(1) AS row_count "
        f"FROM `{config.MODEX_FIVETRAN_FULL_TABLE}`"
    )
    print(json.dumps(r, indent=2, default=str))

    print("\n=== Face 1 events by type ===")
    r2 = _run_bq(
        f"SELECT event_type AS label, COUNT(1) AS value "
        f"FROM `{config.MODEX_CODEBASE_LOGS_FULL_TABLE}` "
        f"GROUP BY event_type ORDER BY value DESC"
    )
    print(json.dumps(r2, indent=2, default=str))

    print("\n=== Memory timeline ===")
    mem = await get_memory_timeline()
    print(f"status={mem.get('status')} count={len(mem.get('memories', []))}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
