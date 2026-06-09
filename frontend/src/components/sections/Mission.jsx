import { useState } from "react";
import { Section, SectionHead } from "../ui/Section";
import { Reveal } from "../ui/Reveal";
import { MissionIcon } from "../../lib/icons";
import { QUICK_MISSIONS } from "../../lib/theme";
import { runMission } from "../../hooks";
import { AgentAnswer } from "../ui/AgentAnswer";

function formatElapsed(ms) {
  if (!ms) return "";
  const s = (ms / 1000).toFixed(1);
  return `${s}s`;
}

export function Mission() {
  const [prompt, setPrompt] = useState("");
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  async function run(text) {
    const p = (text ?? prompt).trim();
    if (!p || running) return;
    setPrompt(p);
    setRunning(true);
    setError(null);
    setResult(null);
    try {
      const res = await runMission(p);
      setResult(res);
    } catch (e) {
      setError(e.message || "Mission failed");
    } finally {
      setRunning(false);
    }
  }

  const demoMissions = QUICK_MISSIONS.filter((m) => m.demo);
  const extraMissions = QUICK_MISSIONS.filter((m) => !m.demo);

  return (
    <Section id="mission" theme="dark" aurora>
      <SectionHead
        eyebrow="Face 2 · ask the centralized memory guide"
        title='Questions the bus can <span class="grad-text">actually answer</span>'
        lead="Not an orchestrator demo — three real jobs: answer from shared memory, operate Fivetran-managed connectors, act only after you approve. Click a scenario (30–90s)."
      />

      <p className="mission-demo-hint">
        <strong>Face 1 proved capture (MCP).</strong> Face 2 proves retrieval + Fivetran ops.
        Start with <em>Hydrate me</em> or <em>Why this stack?</em> — cited answers from session + GitHub.
      </p>

      <div className="mission-quick">
        {demoMissions.map((m) => (
          <button
            key={m.id}
            className="mission-chip mission-chip-demo"
            onClick={() => run(m.prompt)}
            disabled={running}
          >
            <MissionIcon id={m.icon} size={18} />
            <span>
              <strong>{m.label}</strong>
              <em>{m.desc}</em>
            </span>
            <span className="mission-chip-badge">Demo</span>
          </button>
        ))}
      </div>

      {extraMissions.length > 0 && (
        <div className="mission-quick mission-quick-secondary">
          {extraMissions.map((m) => (
            <button key={m.id} className="mission-chip" onClick={() => run(m.prompt)} disabled={running}>
              <MissionIcon id={m.icon} size={18} />
              <span>
                <strong>{m.label}</strong>
                <em>{m.desc}</em>
              </span>
            </button>
          ))}
        </div>
      )}

      <Reveal className="mission-console">
        <div className="mission-input-row">
          <textarea
            className="mission-input scrollbar-thin"
            placeholder="e.g. Did the team pick PostgreSQL or MongoDB, and why? Cross-reference the session decision with the GitHub PR review synced via Fivetran."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) run(); }}
            rows={3}
          />
          <button className="btn btn-primary mission-run" onClick={() => run()} disabled={running || !prompt.trim()}>
            {running ? "Asking…" : "Ask the guide"}
            {!running && <svg width="15" height="15" viewBox="0 0 16 16" fill="none"><path d="M3 8h9M9 4l4 4-4 4" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" /></svg>}
          </button>
        </div>

        {running && (
          <div className="mission-out anim-fade-up">
            <div className="mission-thinking">
              <span className="mt-dot" /><span className="mt-dot" /><span className="mt-dot" />
              <span className="mission-thinking-label">
                Querying centralized memory &amp; Fivetran connectors… (30–90s)
              </span>
            </div>
          </div>
        )}

        {!running && error && (
          <div className="mission-out anim-fade-up">
            <div className="mission-error">
              ⚠ {error}
              <span className="mission-error-sub">
                The live agent runs on Cloud Run with gemini-2.5-flash. If this persists, try a shorter demo prompt.
              </span>
            </div>
          </div>
        )}

        {!running && result && (
          <div className="mission-out anim-fade-up">
            {result.trace?.length > 0 && (
              <div className="mission-trace">
                <span className="mission-trace-label mono">
                  agent trace {result.elapsedMs ? `· ${formatElapsed(result.elapsedMs)}` : ""}
                </span>
                <div className="mission-trace-steps">
                  {result.trace.map((t) => (
                    <div key={t.step} className="trace-step">
                      <span className="trace-num">{t.step}</span>
                      <span className="trace-agent">{t.agent}</span>
                      <span className="trace-action">{t.action}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            <div className="mission-answer">
              <AgentAnswer content={result.answer} />
            </div>
          </div>
        )}
      </Reveal>
    </Section>
  );
}
