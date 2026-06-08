import { useState, useEffect, useCallback } from "react";
import { Panel } from "../ui/Panel";
import { MissionIcon, EventIcon } from "../../lib/icons";
import { QUICK_MISSIONS } from "../../lib/theme";
import { runMission } from "../../hooks";

export function MissionDeck({ initialPrompt, onPromptConsumed }) {
  const [prompt, setPrompt] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (initialPrompt) {
      setPrompt(initialPrompt);
      onPromptConsumed?.();
    }
  }, [initialPrompt, onPromptConsumed]);

  const send = useCallback(async () => {
    if (!prompt.trim() || loading) return;
    const q = prompt.trim();
    setPrompt("");
    setMessages((m) => [...m, { role: "user", text: q, ts: Date.now() }]);
    setLoading(true);
    try {
      const result = await runMission(q);
      const text = result.texts.filter((t) => t.length > 20).slice(-1)[0]
        || result.texts.join("\n") || "Agents completed without text response.";
      setMessages((m) => [...m, { role: "agent", text, tools: result.toolCalls, ts: Date.now() }]);
    } catch (e) {
      setMessages((m) => [...m, { role: "agent", text: `Mission failed: ${e.message}`, tools: [], ts: Date.now() }]);
    } finally {
      setLoading(false);
    }
  }, [prompt, loading]);

  return (
    <section id="mission" className="ui-mission-deck animate-in delay-6">
      <Panel title="Quick missions" subtitle="One-click prompts for demo">
        <div className="ui-mission-grid">
          {QUICK_MISSIONS.map((m) => (
            <button key={m.id} type="button" className="ui-mission-tile" onClick={() => setPrompt(m.prompt)}>
              <MissionIcon id={m.icon} size={22} />
              <span className="ui-mission-tile-label">{m.label}</span>
              <span className="ui-mission-tile-desc">{m.desc}</span>
            </button>
          ))}
        </div>
      </Panel>

      <Panel title="Mission console" subtitle="Face 2 · ADK agent team" className="ui-console-panel">
        <div className="ui-console-body scrollbar-thin">
          {messages.length === 0 && !loading && (
            <div className="ui-console-empty">
              <div className="ui-console-empty-ring" />
              <h3>Run a multi-agent mission</h3>
              <p>Ask about team decisions, sync freshness, or session handoff — agents delegate and cite provenance.</p>
            </div>
          )}
          {messages.map((m, i) => (
            <div key={i} className={`ui-bubble ui-bubble-${m.role}`}>
              <div className="ui-bubble-label">{m.role === "user" ? "You" : "Mission Control"}</div>
              <div className="ui-bubble-text">{m.text}</div>
              {m.tools?.length > 0 && (
                <div className="ui-bubble-tools">
                  {m.tools.map((t) => (
                    <span key={t} className="ui-bubble-tool">
                      <EventIcon type="tool" size={10} />{t}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div className="ui-bubble ui-bubble-agent ui-bubble-loading">
              <div className="ui-typing"><span /><span /><span /></div>
              <span>Delegating to specialists…</span>
            </div>
          )}
        </div>
        <div className="ui-console-input">
          <textarea
            rows={2}
            className="ui-console-textarea font-mono"
            placeholder="What architecture decisions has the team made? Cite _fivetran_synced…"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } }}
            disabled={loading}
          />
          <button type="button" className="ui-console-send" onClick={send} disabled={loading || !prompt.trim()}>
            Run mission
          </button>
        </div>
      </Panel>
    </section>
  );
}
