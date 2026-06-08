import { Section } from "../ui/Section";
import { Reveal, RevealGroup } from "../ui/Reveal";

const PAINS = [
  {
    k: "01",
    title: "Context dies at session end",
    body: "Your AI agent's reasoning — why it chose this library, what it ruled out — evaporates the moment the chat closes. Nobody else ever sees it.",
    tone: "sky",
  },
  {
    k: "02",
    title: "Teams relitigate settled calls",
    body: "A fresh agent re-proposes MongoDB three weeks after the team rejected it in a PR review. The same dead-ends get explored again and again.",
    tone: "rose",
  },
  {
    k: "03",
    title: "Every onboarding starts at zero",
    body: "New devs and new agent sessions rediscover the same gotchas from scratch — hours lost per session, multiplied across the whole team.",
    tone: "violet",
  },
];

export function Problem() {
  return (
    <Section id="problem" theme="light">
      <div className="problem-top">
        <Reveal>
          <div className="eyebrow">The gap</div>
          <h2 className="section-title">
            15 developers. 15 AI agents.
            <br />
            <span className="grad-text">Zero shared memory.</span>
          </h2>
        </Reveal>
        <Reveal className="problem-callout" delay={60}>
          <p>
            Git and PRs record <strong>what</strong> changed. But the <strong>why</strong> —
            the decisions, the trade-offs, the approaches that were tried and rejected — lives
            in ephemeral chats, scattered reviews, and people&apos;s heads. Ungoverned.
            Unsearchable. Gone by Monday.
          </p>
        </Reveal>
      </div>

      <RevealGroup className="problem-grid">
        {PAINS.map((p) => (
          <Reveal key={p.k} className={`problem-card card card-hover tone-${p.tone}`}>
            <span className="problem-k mono">{p.k}</span>
            <h3>{p.title}</h3>
            <p>{p.body}</p>
          </Reveal>
        ))}
      </RevealGroup>
    </Section>
  );
}
