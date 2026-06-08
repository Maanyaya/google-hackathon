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
  orchestrator_agent: { letter: "MC", short: "Hub" },
  ingestion_agent: { letter: "DS", short: "Sync" },
  knowledge_agent: { letter: "SM", short: "Memory" },
  lineage_agent: { letter: "DP", short: "Trace" },
  transformation_agent: { letter: "KS", short: "Struct" },
  action_agent: { letter: "TB", short: "Broadcast" },
  guardian_agent: { letter: "AG", short: "Govern" },
};

export const QUICK_MISSIONS = [
  { id: "handoff", label: "Session handoff", desc: "Cursor → Antigravity replay", icon: "handoff", prompt: "What did the last Cursor agent do on github.com/demo/api-service? What should a new Antigravity agent know?" },
  { id: "pipeline", label: "Pipeline health", desc: "Fivetran MCP status", icon: "pipeline", prompt: "Check Fivetran connections in group solve_unhurt. Is stowed_register synced?" },
  { id: "freshness", label: "Memory sync", desc: "Face 1 vs Fivetran bus", icon: "freshness", prompt: "Compare Face 1 codebase_logs vs Fivetran modex_logs. Cite _fivetran_synced." },
  { id: "decisions", label: "Team decisions", desc: "Architecture provenance", icon: "decision", prompt: "List architecture decisions this week from shared memory with provenance." },
  { id: "lineage", label: "Lineage", desc: "Source → BigQuery", icon: "lineage", prompt: "Show source-to-destination lineage from Platform Connector metadata." },
  { id: "export", label: "Standup export", desc: "GCS after Guardian OK", icon: "export", prompt: "Prepare a team standup summary of recent decisions and export to GCS after I approve." },
];

export const NAV = [
  { id: "overview", label: "Overview" },
  { id: "agents", label: "Agents" },
  { id: "memory", label: "Memory" },
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
