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
  orchestrator_agent: { letter: "MC", short: "Plan + Govern" },
  memory_agent: { letter: "SM", short: "Context pack" },
  pipeline_agent: { letter: "DP", short: "Fivetran ops" },
  action_agent: { letter: "TB", short: "Broadcast" },
};

export const QUICK_MISSIONS = [
  { id: "handoff", label: "Hydrate me", desc: "Cold-start → warm-start", icon: "handoff", prompt: "I'm a new agent on github.com/demo/api-service. Use get_team_context to brief me: what has the team decided, what did they reject, and what gotchas exist? Cite PRs and timestamps." },
  { id: "decisions", label: "Why this stack?", desc: "Session ↔ GitHub PR", icon: "decision", prompt: "Did the team pick PostgreSQL or MongoDB, and why? Cross-reference the coding-agent decision with the GitHub PR and reviewer reasoning synced via Fivetran." },
  { id: "freshness", label: "Make memory fresh", desc: "Agent operates Fivetran", icon: "freshness", prompt: "Is our shared memory stale? Check the GitHub connection's last sync, and if needed ask me to approve a sync, then prove freshness improved with _fivetran_synced." },
  { id: "pipeline", label: "Pipeline health", desc: "Fivetran MCP status", icon: "pipeline", prompt: "Check Fivetran connections in group solve_unhurt — is the GitHub connector and stowed_register synced and healthy?" },
  { id: "lineage", label: "Lineage", desc: "Source → BigQuery", icon: "lineage", prompt: "Trace lineage: how does a GitHub PR become a row in our shared decision memory? Use Platform Connector metadata." },
  { id: "export", label: "Standup export", desc: "GCS after approval", icon: "export", prompt: "Prepare a team standup summary of this week's decisions (with provenance) and export to GCS after I approve." },
];

export const NAV = [
  { id: "architecture", label: "Architecture" },
  { id: "agents", label: "Agents" },
  { id: "pack", label: "Context pack" },
  { id: "decisions", label: "Decisions" },
  { id: "pipelines", label: "Pipelines" },
  { id: "mission", label: "Mission" },
];

export const CHART_TOOLTIP = {
  background: "rgba(12, 16, 28, 0.96)",
  border: "1px solid rgba(255,255,255,0.08)",
  borderRadius: 12,
  color: "#F0F3FA",
  fontSize: 12,
  boxShadow: "0 12px 40px rgba(0,0,0,0.45)",
};
