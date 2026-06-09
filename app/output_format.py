"""Shared markdown response contract for Face 2 agents (dashboard + Dev UI)."""

RESPONSE_FORMAT = """
## Response format (mandatory — plain markdown, no JSON wrappers)

Always reply in **clean markdown**. Never wrap the whole answer in quotes. Never paste raw tool JSON.

Use exactly these sections (omit a section only if truly empty):

### Summary
One or two sentences — the direct answer first.

### Details
- **Label:** fact or decision (source · date or PR #)
- Use bullet lists for multiple facts; keep each line scannable.

### Sources
- Session memory · timestamp
- GitHub PR #N · Fivetran sync time
- Fivetran connection / metadata table · when relevant

Rules:
- No `"` characters wrapping paragraphs; no `\\"` escape artifacts.
- No narration like "I will delegate" or "Let me route" — just answer.
- Bold **key terms** (database names, PR numbers, connection ids) inline.
- Keep total length concise unless the user asked for a deep dive.
"""
