import { Section, SectionHead } from "../ui/Section";
import { Reveal } from "../ui/Reveal";

function FaceIcon({ kind }) {
  if (kind === "capture") {
    return (
      <svg width="26" height="26" viewBox="0 0 24 24" fill="none">
        <rect x="2.5" y="4" width="19" height="13" rx="2.5" stroke="currentColor" strokeWidth="1.6" />
        <path d="M7 9l2.5 2.5L7 14M12 14h5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M8.5 20.5h7" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
      </svg>
    );
  }
  return (
    <svg width="26" height="26" viewBox="0 0 24 24" fill="none">
      <circle cx="12" cy="7" r="3.2" stroke="currentColor" strokeWidth="1.6" />
      <circle cx="5.5" cy="17" r="2.6" stroke="currentColor" strokeWidth="1.6" />
      <circle cx="18.5" cy="17" r="2.6" stroke="currentColor" strokeWidth="1.6" />
      <path d="M10 9.5L6.8 14.6M14 9.5l3.2 5.1M8 17h8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  );
}

const STEPS = [
  { n: 1, text: "You code in your IDE. Face 1's MCP server captures the decision and the why — including what you rejected." },
  { n: 2, text: "Fivetran syncs that reasoning (plus GitHub PRs & reviews) into BigQuery — the trusted memory bus. No glue code." },
  { n: 3, text: "Face 2's Gemini agents cross-reference it all and build a cited context pack — operating Fivetran and governing writes." },
  { n: 4, text: "A new session calls load_context and starts warm — with everything the team already knows. The loop closes." },
];

export function Architecture() {
  return (
    <Section id="architecture" theme="dark" aurora>
      <SectionHead
        eyebrow="The architecture · why MoDeX exists"
        title='Two faces, <span class="grad-text">one shared brain</span>'
        lead="MoDeX has two faces. Face 1 captures reasoning where your AI agents already work — inside the IDE. Face 2 is a deployed team of Gemini agents that serves it back, operates the data, and acts. Fivetran + BigQuery are the trusted memory bus between them."
      />

      <Reveal className="arch-stage">
        {/* FACE 1 */}
        <div className="arch-face arch-face-1">
          <div className="arch-face-top">
            <span className="arch-face-badge">Face 1 · capture</span>
            <span className="arch-face-ico"><FaceIcon kind="capture" /></span>
          </div>
          <h3 className="arch-face-name">Developer Edge</h3>
          <p className="arch-face-sub">An MCP server inside your coding agent</p>
          <ul className="arch-face-list">
            <li>Runs in <strong>Cursor · Antigravity · Windsurf</strong></li>
            <li>Captures decisions <em>and</em> rejected approaches as you code</li>
            <li>Governed — your team's context never leaks to outsiders</li>
          </ul>
          <div className="arch-face-foot">
            <code>append_codebase_log()</code>
            <code>load_context()</code>
          </div>
        </div>

        {/* BRIDGE */}
        <div className="arch-bridge">
          <div className="arch-arrow arch-arrow-r" aria-hidden>
            <svg width="100%" height="14" viewBox="0 0 60 14" preserveAspectRatio="none" fill="none"><path d="M0 7h52M48 2l6 5-6 5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" /></svg>
          </div>
          <div className="arch-bridge-card">
            <span className="arch-bridge-tag">the memory bus</span>
            <div className="arch-bridge-item tone-teal"><span className="ab-dot" />Fivetran</div>
            <div className="arch-bridge-plus">+</div>
            <div className="arch-bridge-item tone-amber"><span className="ab-dot" />BigQuery</div>
          </div>
          <div className="arch-arrow arch-arrow-r" aria-hidden>
            <svg width="100%" height="14" viewBox="0 0 60 14" preserveAspectRatio="none" fill="none"><path d="M0 7h52M48 2l6 5-6 5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" /></svg>
          </div>
        </div>

        {/* FACE 2 */}
        <div className="arch-face arch-face-2">
          <div className="arch-face-top">
            <span className="arch-face-badge">Face 2 · serve &amp; act</span>
            <span className="arch-face-ico"><FaceIcon kind="serve" /></span>
          </div>
          <h3 className="arch-face-name">Agent Platform</h3>
          <p className="arch-face-sub">Google ADK + Gemini · deployed on Cloud Run</p>
          <ul className="arch-face-list">
            <li><strong>Mission Control</strong> orchestrates 3 specialist agents</li>
            <li>Builds the cited context pack; operates Fivetran pipelines</li>
            <li>Governs every write — human-in-the-loop approval</li>
          </ul>
          <div className="arch-face-foot">
            <code>Gemini</code>
            <code>Google ADK</code>
            <code>MCP tools</code>
          </div>
        </div>
      </Reveal>

      {/* THE LOOP */}
      <Reveal className="arch-loop">
        <span className="arch-loop-label">How the loop works</span>
        <div className="arch-steps">
          {STEPS.map((s) => (
            <div className="arch-step" key={s.n}>
              <span className="arch-step-n">{s.n}</span>
              <p>{s.text}</p>
            </div>
          ))}
        </div>
      </Reveal>
    </Section>
  );
}
