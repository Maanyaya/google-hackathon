import { useState, useEffect } from "react";
import "./index.css";
import { useDashboardData, runMission } from "./hooks";
import {
  BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid, Legend,
} from "recharts";
import {
  Brain, Database, Search, GitBranch, Layers, Shield,
  Activity, RefreshCw, Send, ChevronRight, Clock,
  BarChart3, PieChartIcon, Zap, Globe, Server, ArrowRight,
} from "lucide-react";

const COLORS = ["#6366f1", "#06b6d4", "#10b981", "#f59e0b", "#8b5cf6", "#ef4444", "#ec4899", "#14b8a6"];

const AGENT_ICONS = {
  brain: Brain, database: Database, search: Search,
  "git-branch": GitBranch, layers: Layers, shield: Shield, send: Send,
};

// ── Header ──────────────────────────────────────────────────────────────────

function Header({ overview }) {
  return (
    <header className="border-b border-[var(--border)] px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
            <Zap className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight">
              {overview?.product_name || "MoDeX — Memory of Codex"}
            </h1>
            <p className="text-xs text-[var(--text-secondary)]">
              {overview?.tagline || "Shared reasoning memory for AI coding teams"}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-6 text-sm">
          <div className="flex items-center gap-2">
            <span className="status-dot green" />
            <span className="text-[var(--text-secondary)]">{overview?.agent_count || 7} Agents Live</span>
          </div>
          <div className="flex items-center gap-2">
            <Globe className="w-4 h-4 text-[var(--text-secondary)]" />
            <span className="text-[var(--text-secondary)]">{overview?.region || "asia-south1"}</span>
          </div>
          <div className="flex items-center gap-2">
            <Server className="w-4 h-4 text-[var(--text-secondary)]" />
            <span className="text-[var(--text-secondary)]">Cloud Run</span>
          </div>
        </div>
      </div>
    </header>
  );
}

// ── Agent Topology ──────────────────────────────────────────────────────────

function AgentTopology({ agents }) {
  if (!agents) return null;
  const orch = agents.find((a) => a.id === "orchestrator_agent");
  const specialists = agents.filter((a) => a.id !== "orchestrator_agent");

  return (
    <div className="card glow-border">
      <div className="card-header flex items-center gap-2">
        <Activity className="w-4 h-4" /> Agent Architecture
      </div>
      <div className="flex flex-col items-center gap-4">
        {orch && <AgentNode agent={orch} isOrch />}
        <div className="flex items-center gap-1 text-[var(--text-secondary)]">
          <ChevronRight className="w-3 h-3" />
          <span className="text-xs">delegates to</span>
          <ChevronRight className="w-3 h-3" />
        </div>
        <div className="grid grid-cols-3 gap-3 w-full lg:grid-cols-6">
          {specialists.map((a) => <AgentNode key={a.id} agent={a} />)}
        </div>
      </div>
    </div>
  );
}

function AgentNode({ agent, isOrch }) {
  const Icon = AGENT_ICONS[agent.icon] || Brain;
  return (
    <div
      className={`rounded-lg p-3 text-center border transition-all hover:scale-105 ${
        isOrch ? "border-indigo-500/50 bg-indigo-500/10" : "border-[var(--border)] bg-[var(--bg-primary)]"
      }`}
    >
      <div
        className="w-8 h-8 rounded-lg mx-auto mb-2 flex items-center justify-center"
        style={{ backgroundColor: agent.color + "20" }}
      >
        <Icon className="w-4 h-4" style={{ color: agent.color }} />
      </div>
      <div className="text-sm font-semibold">{agent.label}</div>
      <div className="text-[10px] text-[var(--text-secondary)] mt-1 leading-tight">
        {agent.description.split("—")[0]}
      </div>
      {agent.mcp && (
        <div className="mt-2 text-[9px] px-2 py-0.5 rounded-full bg-[var(--bg-primary)] border border-[var(--border)] text-[var(--text-secondary)] inline-block">
          {agent.mcp}
        </div>
      )}
    </div>
  );
}

// ── Pipeline Cards ──────────────────────────────────────────────────────────

function PipelineCards({ data }) {
  if (!data?.pipelines) return null;
  return (
    <div className="card">
      <div className="card-header flex items-center gap-2">
        <Database className="w-4 h-4" /> Fivetran Pipelines
      </div>
      <div className="grid grid-cols-1 gap-3">
        {data.pipelines.map((p) => (
          <div
            key={p.id}
            className="flex items-center justify-between p-3 rounded-lg bg-[var(--bg-primary)] border border-[var(--border)]"
          >
            <div className="flex items-center gap-3">
              <span className={`status-dot ${p.paused ? "yellow" : p.status === "scheduled" ? "green" : "red"}`} />
              <div>
                <div className="text-sm font-medium">{p.name || p.id}</div>
                <div className="text-xs text-[var(--text-secondary)]">{p.service}</div>
              </div>
            </div>
            <div className="text-right">
              <div className="text-xs font-medium">{p.paused ? "Paused" : p.status}</div>
              {p.succeeded_at && (
                <div className="text-[10px] text-[var(--text-secondary)]">
                  Last sync: {new Date(p.succeeded_at).toLocaleString()}
                </div>
              )}
            </div>
          </div>
        ))}
        {data.pipelines.length === 0 && (
          <div className="text-sm text-[var(--text-secondary)] text-center py-4">No pipelines found</div>
        )}
      </div>
    </div>
  );
}

// ── Freshness Cards ─────────────────────────────────────────────────────────

function FreshnessCards({ data }) {
  if (!data) return null;
  const mt = data.main_table;
  const f1 = data.face1_memory;
  const md = data.metadata;

  return (
    <div className="card">
      <div className="card-header flex items-center gap-2">
        <Clock className="w-4 h-4" /> Memory Freshness
      </div>
      <div className="grid grid-cols-2 gap-3">
        <FreshnessStat label="Fivetran MoDeX Logs" value={mt?.row_count} sub={mt?.last_synced ? `Synced ${new Date(mt.last_synced).toLocaleString()}` : "—"} />
        <FreshnessStat label="Face 1 Codebase Logs" value={f1?.event_count} sub={f1?.last_event ? `Last ${new Date(f1.last_event).toLocaleString()}` : "—"} />
        <FreshnessStat label="Pipeline Metadata" value={md?.event_count} sub={md?.last_event ? `Last ${new Date(md.last_event).toLocaleString()}` : "—"} />
        {data.analytics_tables?.map((t) => (
          <FreshnessStat key={t.table} label={t.table} value={t.row_count ?? "—"} sub="analytics" />
        ))}
      </div>
    </div>
  );
}

function FreshnessStat({ label, value, sub }) {
  return (
    <div className="p-3 rounded-lg bg-[var(--bg-primary)] border border-[var(--border)]">
      <div className="text-2xl font-bold">{value ?? "—"}</div>
      <div className="text-xs font-medium mt-1">{label}</div>
      <div className="text-[10px] text-[var(--text-secondary)] mt-0.5 truncate">{sub}</div>
    </div>
  );
}

// ── Charts ──────────────────────────────────────────────────────────────────

function ChartPanel({ title, icon, chartData, chartType }) {
  if (!chartData?.data) return null;
  const Icon = icon;
  return (
    <div className="card">
      <div className="card-header flex items-center gap-2">
        <Icon className="w-4 h-4" /> {title}
      </div>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          {chartType === "pie" ? (
            <PieChart>
              <Pie
                data={chartData.data}
                dataKey="value"
                nameKey="label"
                cx="50%"
                cy="50%"
                outerRadius={90}
                label={({ label, value }) => `${label}: ${value}`}
              >
                {chartData.data.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 8, color: "#f1f5f9" }} />
            </PieChart>
          ) : (
            <BarChart data={chartData.data} margin={{ top: 5, right: 20, left: 0, bottom: 60 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="label" tick={{ fontSize: 11, fill: "#94a3b8" }} angle={-35} textAnchor="end" />
              <YAxis tick={{ fontSize: 11, fill: "#94a3b8" }} />
              <Tooltip contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 8, color: "#f1f5f9" }} />
              <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                {chartData.data.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  );
}

// ── Timeline ────────────────────────────────────────────────────────────────

function Timeline({ data }) {
  if (!data?.events) return null;
  return (
    <div className="card">
      <div className="card-header flex items-center gap-2">
        <Activity className="w-4 h-4" /> Pipeline Event Log
      </div>
      <div className="max-h-64 overflow-y-auto scrollbar-thin space-y-2">
        {data.events.slice(0, 15).map((ev, i) => (
          <div key={i} className="flex items-start gap-3 p-2 rounded-lg bg-[var(--bg-primary)] text-xs">
            <span className={`status-dot mt-1 ${ev.event === "WARNING" ? "yellow" : ev.event === "SEVERE" ? "red" : "green"}`} />
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <span className="font-medium">{ev.message_event || ev.event}</span>
                <span className="text-[var(--text-secondary)] text-[10px]">
                  {ev.time_stamp ? new Date(ev.time_stamp).toLocaleString() : ""}
                </span>
              </div>
              {ev.message_data && (
                <div className="text-[var(--text-secondary)] mt-0.5 truncate">{ev.message_data}</div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Lineage View ────────────────────────────────────────────────────────────

function LineageView({ data }) {
  if (!data?.lineage?.length) return null;
  return (
    <div className="card">
      <div className="card-header flex items-center gap-2">
        <GitBranch className="w-4 h-4" /> Data Lineage
      </div>
      <div className="space-y-2">
        {data.lineage.map((l, i) => (
          <div key={i} className="flex items-center gap-3 p-2 rounded-lg bg-[var(--bg-primary)] text-sm">
            <span className="px-2 py-1 rounded bg-cyan-500/10 text-cyan-400 text-xs font-mono">
              {l.source_table || "source"}
            </span>
            <ArrowRight className="w-4 h-4 text-[var(--text-secondary)]" />
            <span className="px-2 py-1 rounded bg-green-500/10 text-green-400 text-xs font-mono">
              {l.destination_table || "destination"}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Memory Timeline (Face 1) ────────────────────────────────────────────────

function MemoryTimeline({ data }) {
  if (!data?.memories?.length) return null;
  const typeColors = {
    decision: "text-amber-400",
    file_edit: "text-cyan-400",
    error: "text-red-400",
    session_end: "text-indigo-400",
    session_start: "text-green-400",
  };
  return (
    <div className="card">
      <div className="card-header flex items-center gap-2">
        <Brain className="w-4 h-4" /> Shared Memory Timeline (Face 1)
      </div>
      <div className="max-h-64 overflow-y-auto scrollbar-thin space-y-2">
        {data.memories.slice(0, 12).map((m, i) => (
          <div key={i} className="flex items-start gap-3 p-2 rounded-lg bg-[var(--bg-primary)] text-xs">
            <span className={`font-mono text-[10px] uppercase ${typeColors[m.event_type] || "text-[var(--text-secondary)]"}`}>
              {m.event_type}
            </span>
            <div className="flex-1 min-w-0">
              <div className="font-medium truncate">{m.summary}</div>
              <div className="text-[var(--text-secondary)] mt-0.5">
                {m.developer_id} · {m.agent_tool}
                {m.file_path ? ` · ${m.file_path}` : ""}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Chat Panel ──────────────────────────────────────────────────────────────

function ChatPanel({ initialPrompt, onPromptConsumed }) {
  const [prompt, setPrompt] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (initialPrompt) {
      setPrompt(initialPrompt);
      onPromptConsumed?.();
    }
  }, [initialPrompt, onPromptConsumed]);

  const send = async () => {
    if (!prompt.trim() || loading) return;
    const q = prompt.trim();
    setPrompt("");
    setMessages((m) => [...m, { role: "user", text: q }]);
    setLoading(true);
    try {
      const result = await runMission(q);
      const agentText = result.texts.filter(t => t.length > 20).slice(-1)[0] || result.texts.join("\n") || "No response.";
      setMessages((m) => [
        ...m,
        {
          role: "agent",
          text: agentText,
          tools: result.toolCalls,
        },
      ]);
    } catch (e) {
      setMessages((m) => [...m, { role: "agent", text: `Error: ${e.message}` }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card flex flex-col h-full">
      <div className="card-header flex items-center gap-2">
        <Send className="w-4 h-4" /> Agent Mission Console
      </div>
      <div className="flex-1 overflow-y-auto scrollbar-thin space-y-3 mb-3 min-h-[200px] max-h-[400px]">
        {messages.length === 0 && (
          <div className="text-sm text-[var(--text-secondary)] text-center py-8">
            Ask the agents a question.<br />
            <span className="text-xs">e.g. "What did the team decide about PostgreSQL vs MongoDB? Cite sync time."</span>
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`p-3 rounded-lg text-sm ${m.role === "user" ? "bg-indigo-500/10 border border-indigo-500/30 ml-8" : "bg-[var(--bg-primary)] border border-[var(--border)] mr-4"}`}>
            <div className="text-[10px] font-semibold text-[var(--text-secondary)] mb-1 uppercase">
              {m.role === "user" ? "You" : "Agent"}
            </div>
            <div className="whitespace-pre-wrap">{m.text}</div>
            {m.tools?.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1">
                {m.tools.map((t, j) => (
                  <span key={j} className="text-[9px] px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                    {t}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="flex items-center gap-2 text-sm text-[var(--text-secondary)] p-3">
            <RefreshCw className="w-4 h-4 animate-spin" /> Agents working...
          </div>
        )}
      </div>
      <div className="flex gap-2">
        <input
          className="flex-1 bg-[var(--bg-primary)] border border-[var(--border)] rounded-lg px-3 py-2 text-sm outline-none focus:border-indigo-500 transition-colors"
          placeholder="Ask the agents..."
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          disabled={loading}
        />
        <button
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
          onClick={send}
          disabled={loading || !prompt.trim()}
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}

// ── Quick Actions ───────────────────────────────────────────────────────────

function QuickActions({ onSelect }) {
  const actions = [
    { label: "Session handoff", prompt: "What did the last Cursor agent do on github.com/demo/api-service? What should a new Antigravity agent know?" },
    { label: "Pipeline health", prompt: "Check Fivetran connections in group solve_unhurt. Is stowed_register synced?" },
    { label: "Memory freshness", prompt: "Compare Face 1 codebase_logs vs Fivetran modex_logs. Cite _fivetran_synced." },
    { label: "Engineering decisions", prompt: "List architecture decisions this week from shared memory with provenance." },
    { label: "Data lineage", prompt: "Show source-to-destination lineage from Platform Connector metadata." },
    { label: "Export report", prompt: "Prepare a team standup summary of recent decisions and export to GCS after I approve." },
  ];

  return (
    <div className="card">
      <div className="card-header">Quick Missions</div>
      <div className="flex flex-wrap gap-2">
        {actions.map((a, i) => (
          <button
            key={i}
            className="text-xs px-3 py-1.5 rounded-full bg-[var(--bg-primary)] border border-[var(--border)] hover:border-indigo-500/50 hover:bg-indigo-500/5 transition-all"
            onClick={() => onSelect?.(a.prompt)}
            title={a.prompt}
          >
            {a.label}
          </button>
        ))}
      </div>
    </div>
  );
}

// ── Main App ────────────────────────────────────────────────────────────────

export default function App() {
  const [missionPrompt, setMissionPrompt] = useState("");
  const { data: overview } = useDashboardData("/api/dashboard/overview");
  const { data: topology } = useDashboardData("/api/dashboard/topology");
  const { data: pipelines } = useDashboardData("/api/dashboard/pipelines");
  const { data: freshness } = useDashboardData("/api/dashboard/freshness");
  const { data: memory } = useDashboardData("/api/dashboard/memory", 30000);
  const { data: activities } = useDashboardData("/api/dashboard/charts/activities");
  const { data: classLevels } = useDashboardData("/api/dashboard/charts/class-levels");
  const { data: majors } = useDashboardData("/api/dashboard/charts/majors");
  const { data: states } = useDashboardData("/api/dashboard/charts/states");
  const { data: timeline } = useDashboardData("/api/dashboard/timeline");
  const { data: lineage } = useDashboardData("/api/dashboard/lineage");

  return (
    <div className="min-h-screen">
      <Header overview={overview} />

      <main className="p-6">
        <div className="mb-6">
          <AgentTopology agents={topology?.agents} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <PipelineCards data={pipelines} />
          <FreshnessCards data={freshness} />
          <Timeline data={timeline} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <MemoryTimeline data={memory} />
          <ChartPanel title={activities?.title || "Events by Type"} icon={BarChart3} chartData={activities} chartType="bar" />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <ChartPanel title={classLevels?.title || "Events by Agent Tool"} icon={PieChartIcon} chartData={classLevels} chartType="pie" />
          <ChartPanel title={states?.title || "Engineering Decisions"} icon={BarChart3} chartData={states} chartType="bar" />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <div className="space-y-6">
            <LineageView data={lineage} />
            <QuickActions onSelect={setMissionPrompt} />
          </div>
          <ChatPanel
            initialPrompt={missionPrompt}
            onPromptConsumed={() => setMissionPrompt("")}
          />
        </div>
      </main>

      <footer className="border-t border-[var(--border)] px-6 py-3 text-center text-xs text-[var(--text-secondary)]">
        MoDeX · Google Cloud Rapid Agent Hackathon · Fivetran Track · Gemini ADK + Fivetran MCP
      </footer>
    </div>
  );
}
