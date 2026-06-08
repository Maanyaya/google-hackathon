import json
from app.memory_graph import build_context_pack

p = build_context_pack()
print("status:", p["status"])
print("counts:", json.dumps(p["counts"]))
print("connected:", p["freshness"].get("connected_sources"))
print("source statuses:", {s["id"]: s["status"] for s in p.get("sources", [])})
print("--- decisions ---")
for d in p["decisions"]:
    print(f"[{d.get('corroboration')}x] {d['decision'][:46]!r} -> {d.get('source_types')}")
print("--- rejected ---")
for r in p["rejected"]:
    print(f"[{r.get('corroboration')}x] {r['decision'][:46]!r} "
          f"jira={[j.get('key') for j in r.get('jira', [])]} "
          f"slack={[s.get('channel') for s in r.get('slack', [])]}")
print("--- open_questions ---")
for o in p["open_questions"]:
    print(f"[{o.get('corroboration')}x] {o['decision'][:46]!r} "
          f"jira={[j.get('key') for j in o.get('jira', [])]} "
          f"slack={[s.get('channel') for s in o.get('slack', [])]}")
print("--- hydration (first 1400) ---")
print(p["hydration_prompt"][:1400])
