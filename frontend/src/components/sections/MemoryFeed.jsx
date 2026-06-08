import { Panel, Skeleton } from "../ui/Panel";
import { EventIcon } from "../../lib/icons";
import { EVENT_TYPES, AGENT_TOOLS } from "../../lib/theme";
import { fmtRelative, initials } from "../../lib/format";

export function MemoryFeed({ data, loading }) {
  const memories = data?.memories || [];

  return (
    <Panel id="memory" title="Shared memory feed" subtitle="Face 1 codebase_logs · session thread" className="animate-in delay-4">
      {loading && !memories.length ? (
        <div className="ui-memory-skeleton">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-20 rounded-xl mb-3" />
          ))}
        </div>
      ) : memories.length === 0 ? (
        <div className="ui-empty-state">
          <div className="ui-empty-icon">◇</div>
          <p>No session memory yet</p>
          <span>Use Cursor MCP · append_codebase_log to seed events</span>
        </div>
      ) : (
        <div className="ui-memory-feed scrollbar-thin">
          {memories.slice(0, 16).map((m, i) => {
            const ev = EVENT_TYPES[m.event_type] || { label: m.event_type, color: "#8892A8", icon: "default" };
            const tool = AGENT_TOOLS[m.agent_tool] || { label: m.agent_tool, color: "#8892A8", bg: "rgba(255,255,255,0.05)" };
            return (
              <article key={m.event_id || i} className="ui-memory-card" style={{ "--accent": ev.color, animationDelay: `${i * 40}ms` }}>
                <div className="ui-memory-avatar" style={{ background: tool.bg, color: tool.color }}>
                  {initials(m.developer_id)}
                </div>
                <div className="ui-memory-content">
                  <header className="ui-memory-head">
                    <EventIcon type={ev.icon} size={14} />
                    <span className="ui-memory-type" style={{ color: ev.color }}>{ev.label}</span>
                    <span className="ui-memory-tool" style={{ color: tool.color, background: tool.bg }}>{tool.label}</span>
                    <time>{fmtRelative(m.created_at)}</time>
                  </header>
                  <p className="ui-memory-summary">{m.summary}</p>
                  {(m.file_path || m.developer_id) && (
                    <footer className="ui-memory-foot font-mono">
                      {m.developer_id}{m.file_path ? ` · ${m.file_path}` : ""}
                    </footer>
                  )}
                </div>
              </article>
            );
          })}
        </div>
      )}
    </Panel>
  );
}
