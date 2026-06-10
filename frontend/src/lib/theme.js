export const TOKENS = {
  memory: "#E8A317",
  memorySoft: "rgba(232, 163, 23, 0.14)",
  pipeline: "#0DDBBE",
  pipelineSoft: "rgba(13, 219, 190, 0.12)",
  agent: "#9D8DF1",
  agentSoft: "rgba(157, 141, 241, 0.12)",
  code: "#3BCEFF",
  codeSoft: "rgba(59, 206, 255, 0.12)",
  danger: "#FF6B6B",
  success: "#3DDC97",
  warn: "#FFBE4D",
  chart: ["#E8A317", "#0DDBBE", "#9D8DF1", "#3BCEFF", "#FF6B9D", "#3DDC97", "#FFBE4D", "#7C8AFF"],
};

export const EVENT_TYPES = {
  decision: { label: "Decision", color: TOKENS.memory, icon: "decision" },
  file_edit: { label: "Edit", color: TOKENS.code, icon: "file" },
  error: { label: "Error", color: TOKENS.danger, icon: "error" },
  session_start: { label: "Start", color: TOKENS.success, icon: "session" },
  session_end: { label: "End", color: TOKENS.agent, icon: "session" },
  tool_call: { label: "Tool", color: "#7C8AFF", icon: "tool" },
  user_prompt: { label: "Prompt", color: "#8892A8", icon: "prompt" },
};

export const AGENT_TOOLS = {
  cursor: { label: "Cursor", color: "#22D3EE", bg: "rgba(34,211,238,0.12)" },
  antigravity: { label: "Antigravity", color: "#9D8DF1", bg: "rgba(157,141,241,0.12)" },
  windsurf: { label: "Windsurf", color: "#3DDC97", bg: "rgba(61,220,151,0.12)" },
};

export const AGENT_META = {
  orchestrator_agent: { letter: "CM", short: "Routes + governs" },
  memory_agent: { letter: "MA", short: "Memory answers" },
  pipeline_agent: { letter: "FO", short: "Fivetran ops" },
  action_agent: { letter: "GA", short: "Governed export" },
};

/** Face 2 exists for these three answerable jobs — not "orchestrator blah blah". */
export const FACE2_AGENDA = [
  {
    n: 1,
    id: "memory",
    title: "Answer from centralized memory",
    desc: "What did the team decide? Why PostgreSQL not MongoDB? What was rejected? Every answer cites session logs + GitHub PRs synced via Fivetran.",
    examples: [
      "Hydrate a new Cursor session on this repo",
      "Cross-reference a decision with PR #142",
    ],
  },
  {
    n: 2,
    id: "fivetran",
    title: "Operate Fivetran-managed connectors",
    desc: "List, health-check, and sync the pipelines that feed the memory bus — MoDeX logs, GitHub, Platform Connector metadata. The ops layer Fivetran judges expect agents to run.",
    examples: [
      "Is stowed_register synced?",
      "Trace lineage: Sheet → BigQuery → decisions view",
    ],
  },
  {
    n: 3,
    id: "act",
    title: "Act with your approval",
    desc: "Export standup summaries, push to Sheets, or notify the team. Writes never happen silently.",
    examples: [
      "Export this week's decisions to GCS",
      "Push a report row after I approve",
    ],
  },
];

export const QUICK_MISSIONS = [
  {
    id: "handoff",
    label: "Hydrate me",
    desc: "Job 1 · memory answer",
    icon: "handoff",
    demo: true,
    agenda: "memory",
    prompt:
      "I'm a new agent on github.com/demo/api-service. Use get_team_context to brief me: what has the team decided, what did they reject, and what gotchas exist? Cite PR numbers and Fivetran sync timestamps. Be concise.",
  },
  {
    id: "decisions",
    label: "Why this stack?",
    desc: "Job 1 · provenance",
    icon: "decision",
    demo: true,
    agenda: "memory",
    prompt:
      "Did the team pick PostgreSQL or MongoDB, and why? Cross-reference the coding-agent session decision with GitHub PR #142 and the rejected PR #88 — include reviewer quotes and _fivetran_synced timestamps.",
  },
  {
    id: "pipeline",
    label: "Pipeline health",
    desc: "Job 2 · Fivetran ops",
    icon: "pipeline",
    demo: true,
    agenda: "fivetran",
    prompt:
      "Check Fivetran connections in group solve_unhurt — are the GitHub connector and stowed_register (MoDeX logs) synced and healthy? Report last succeeded_at for each.",
  },
  {
    id: "freshness",
    label: "Memory freshness",
    desc: "Read-only audit",
    icon: "freshness",
    prompt:
      "Is our shared memory stale? Check when GitHub and MoDeX logs last synced via Fivetran. Do NOT trigger a sync — just report freshness with timestamps.",
  },
  {
    id: "lineage",
    label: "Lineage",
    desc: "Source → BigQuery",
    icon: "lineage",
    prompt:
      "Trace lineage: how does a GitHub PR become a row in our shared decision memory? Use Platform Connector metadata tables.",
  },
  {
    id: "export",
    label: "Standup export",
    desc: "GCS after approval",
    icon: "export",
    prompt:
      "Prepare a team standup summary of this week's decisions (with provenance) and ask me to approve before exporting to GCS.",
  },
];

export const NAV = [
  { id: "architecture", label: "Architecture" },
  { id: "stack", label: "Stack" },
  { id: "ask", label: "Ask Face 2" },
  { id: "flow", label: "Data flow" },
  { id: "demo", label: "Demo" },
  { id: "agents", label: "Agents" },
  { id: "pack", label: "Context pack" },
  { id: "pipelines", label: "Pipelines" },
];

export const CHART_TOOLTIP = {
  background: "rgba(12, 16, 28, 0.96)",
  border: "1px solid rgba(255,255,255,0.08)",
  borderRadius: 12,
  color: "#F0F3FA",
  fontSize: 12,
  boxShadow: "0 12px 40px rgba(0,0,0,0.45)",
};
