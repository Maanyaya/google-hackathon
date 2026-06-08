import { useState } from "react";
import { Section, SectionHead } from "../ui/Section";
import { Reveal } from "../ui/Reveal";
import { MissionIcon } from "../../lib/icons";
import { QUICK_MISSIONS } from "../../lib/theme";
import { runMission } from "../../hooks";

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

  return (
    <Section id="mission" theme="dark" aurora>
      <SectionHead
        eyebrow="Live mission console"
        title='Ask the team&apos;s <span class="grad-text">shared memory</span> anything'
        lead="Mission Control plans, delegates to specialists, calls real tools (BigQuery, Fivetran, RAG), and gates every write behind approval. This talks to the deployed agents."
      />

      <div className="mission-quick">
        {QUICK_MISSIONS.map((m) => (
          <button key={m.id} className="mission-chip" onClick={() => run(m.prompt)} disabled={running}>
            <MissionIcon id={m.icon} size={18} />
            <span>
              <strong>{m.label}</strong>
              <em>{m.desc}</em>
            </span>
          </button>
        ))}
      </div>

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
            {running ? "Running…" : "Run mission"}
            {!running && <svg width="15" height="15" viewBox="0 0 16 16" fill="none"><path d="M3 8h9M9 4l4 4-4 4" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" /></svg>}
          </button>
        </div>

        {running && (
          <div className="mission-out anim-fade-up">
            <div className="mission-thinking">
              <span className="mt-dot" /><span className="mt-dot" /><span className="mt-dot" />
              <span className="mission-thinking-label">Mission Control is planning &amp; delegating…</span>
            </div>
          </div>
        )}

        {!running && error && (
          <div className="mission-out anim-fade-up">
            <div className="mission-error">⚠ {error}<span className="mission-error-sub">The live agent is reachable on the deployed Cloud Run service.</span></div>
          </div>
        )}

        {!running && result && (
          <div className="mission-out anim-fade-up">
            {result.toolCalls?.length > 0 && (
              <div className="mission-trace">
                <span className="mission-trace-label mono">tool trace</span>
                <div className="mission-trace-chips">
                  {result.toolCalls.map((t, i) => (
                    <span key={i} className="trace-chip">
                      <span className="trace-num">{i + 1}</span>{t}
                    </span>
                  ))}
                </div>
              </div>
            )}
            <div className="mission-answer">
              {(result.texts || []).map((t, i) => <p key={i}>{t}</p>)}
              {!result.texts?.length && <p className="mission-answer-empty">Mission completed — no text response.</p>}
            </div>
          </div>
        )}
      </Reveal>
    </Section>
  );
}
