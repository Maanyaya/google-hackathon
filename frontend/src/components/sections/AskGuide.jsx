/**
 * AskGuide — prominent Face 2 agent console.
 * Placed near the top so it's the first interactive section.
 */
import { useState } from "react";
import { Section, SectionHead } from "../ui/Section";
import { MissionIcon } from "../../lib/icons";
import { QUICK_MISSIONS } from "../../lib/theme";
import { runMission } from "../../hooks";
import { AgentAnswer } from "../ui/AgentAnswer";

function formatElapsed(ms) {
  if (!ms) return "";
  return `${(ms / 1000).toFixed(1)}s`;
}

const DEMO_CHIPS = [
  {
    id: "hydrate",
    label: "Hydrate me",
    icon: "hydrate",
    prompt: "Hydrate me on github.com/Maanyaya/google-hackathon",
  },
  {
    id: "pipeline",
    label: "Pipeline trust",
    icon: "pipeline",
    prompt: "What is the current sync status of the MoDeX logs pipeline? Check the Platform Connector metadata for freshness and lineage.",
  },
  {
    id: "why",
    label: "Why this stack?",
    icon: "reason",
    prompt: "Why was python.exe chosen over a .cmd wrapper for the Antigravity hooks? Cross-reference with any GitHub PR review.",
  },
  {
    id: "trigger",
    label: "Trigger sync",
    icon: "pipeline",
    prompt: "Check the stowed_register connector health. If the MoDeX logs are stale, request approval to trigger a resync.",
  },
];

export function AskGuide() {
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

  const extraChips = (QUICK_MISSIONS || []).filter(
    (m) => !DEMO_CHIPS.find((d) => d.id === m.id)
  );

  return (
    <Section id="ask" theme="dark" aurora>
      <SectionHead
        eyebrow="Face 2 · Central Memory Guide"
        title={`Ask the <span class="grad-text">shared memory bus</span>`}
        lead="Not a chatbot — three real jobs: answer from shared memory, operate Fivetran pipelines, govern actions. Try a demo prompt or write your own (30–90s)."
      />

      {/* quick chips */}
      <div className="ask-chips">
        {DEMO_CHIPS.map((m) => (
          <button
            key={m.id}
            className="ask-chip ask-chip-demo"
            onClick={() => run(m.prompt)}
            disabled={running}
          >
            <MissionIcon id={m.icon} size={18} />
            <span className="ask-chip-label">{m.label}</span>
            <span className="ask-chip-badge">Demo</span>
          </button>
        ))}
        {extraChips.slice(0, 3).map((m) => (
          <button
            key={m.id}
            className="ask-chip"
            onClick={() => run(m.prompt)}
            disabled={running}
          >
            <MissionIcon id={m.icon} size={16} />
            <span className="ask-chip-label">{m.label}</span>
          </button>
        ))}
      </div>

      {/* chat console */}
      <div className="ask-console">
        {/* input */}
        <div className="ask-input-wrap">
          <textarea
            className="ask-input scrollbar-thin"
            placeholder="e.g. Why was FastAPI chosen? What did we reject and why? What's the Fivetran sync status?"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) run();
            }}
            rows={2}
          />
          <button
            className="ask-send btn btn-primary"
            onClick={() => run()}
            disabled={running || !prompt.trim()}
            aria-label="Ask"
          >
            {running ? (
              <span className="ask-send-dots">
                <span /><span /><span />
              </span>
            ) : (
              <svg width="18" height="18" viewBox="0 0 20 20" fill="none" aria-hidden>
                <path d="M3 10h13M12 5l6 5-6 5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            )}
          </button>
        </div>
        <p className="ask-hint">Ctrl/⌘ + Enter to send · responses cite real session logs + GitHub PRs</p>

        {/* output */}
        {running && (
          <div className="ask-out anim-fade-up">
            <div className="ask-thinking">
              <span className="mt-dot" /><span className="mt-dot" /><span className="mt-dot" />
              <span className="ask-thinking-label">
                Querying centralized memory &amp; Fivetran… (30–90s)
              </span>
            </div>
          </div>
        )}

        {!running && error && (
          <div className="ask-out anim-fade-up">
            <div className="ask-error">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden>
                <circle cx="8" cy="8" r="7" stroke="currentColor" strokeWidth="1.4" />
                <path d="M8 5v3M8 11v.5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
              </svg>
              <span>{error}</span>
            </div>
          </div>
        )}

        {!running && result && (
          <div className="ask-out anim-fade-up">
            {result.trace?.length > 0 && (
              <div className="ask-trace">
                <span className="ask-trace-label">
                  agent trace{result.elapsedMs ? ` · ${formatElapsed(result.elapsedMs)}` : ""}
                </span>
                <div className="ask-trace-steps">
                  {result.trace.map((t) => (
                    <div key={t.step} className="ask-trace-step">
                      <span className="trace-num">{t.step}</span>
                      <span className="trace-agent">{t.agent}</span>
                      <span className="trace-action">{t.action}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            <div className="ask-answer">
              <AgentAnswer content={result.answer} />
            </div>
          </div>
        )}
      </div>
    </Section>
  );
}
