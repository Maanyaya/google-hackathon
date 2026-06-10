/**
 * DemoVideo — full MoDeX demo (Face 1 + Fivetran + Face 2).
 */
import { Section, SectionHead } from "../ui/Section";
import { Reveal } from "../ui/Reveal";
import { VideoEmbed } from "../ui/VideoEmbed";

const DEMO_VIDEO_URL = "https://youtu.be/_-O5sinN4qY";

const TIMELINE = [
  {
    t: "0:00",
    label: "Intro — what is MoDeX",
    desc: "The problem: agents forget. MoDeX gives them shared persistent memory on Gemini ADK + Google Cloud + Fivetran.",
  },
  {
    t: "0:50",
    label: "Dashboard scroll — architecture + stack",
    desc: "Two faces, one bus. Google Cloud (ADK, BigQuery, Cloud Run, Secret Manager) + Fivetran MCP with 3 live connectors.",
  },
  {
    t: "1:00",
    label: "Face 1 — MCP in the IDE",
    desc: "Agent A works in Cursor. Decisions captured, context compressed, pushed to GitHub. Memory flows to BigQuery + Sheets.",
  },
  {
    t: "1:40",
    label: "Agent B hydrates",
    desc: "Different developer ID, same repo. load_context pulls Agent A's decisions — zero cold start.",
  },
  {
    t: "2:00",
    label: "Fivetran + BigQuery",
    desc: "Connectors syncing: session logs, GitHub PRs, Platform Connector lineage. Spreadsheet rows visible in BigQuery.",
  },
  {
    t: "2:30",
    label: "Face 2 — Fivetran MCP live",
    desc: "Pipeline trust: agent trace shows list_connections, get_connector_lineage. Data trust — not just data sync.",
  },
  {
    t: "2:50",
    label: "Close",
    desc: "Two agents, one shared brain. Zero cold starts. Try it — link in description.",
  },
];

export function DemoVideo({ videoUrl = "" }) {
  const url = DEMO_VIDEO_URL || videoUrl;

  return (
    <Section id="demo" theme="dark" aurora>
      <SectionHead
        eyebrow="Demo · see MoDeX in action"
        title={`Watch the <span class="grad-text">full demo</span>`}
        lead="Three minutes: dashboard walkthrough, Face 1 MCP in Cursor, agent-to-agent handoff, Fivetran connectors, Face 2 pipeline operations live."
      />

      <Reveal>
        <VideoEmbed
          url={url}
          title="MoDeX — Full Hackathon Demo"
          placeholderTitle="Demo video"
          placeholderLead="Video loading..."
        />
      </Reveal>

      <Reveal className="demo-story-beats">
        {TIMELINE.map((b) => (
          <div key={b.t} className="demo-beat">
            <span className="demo-beat-t">{b.t}</span>
            <div>
              <strong className="demo-beat-label">{b.label}</strong>
              <p className="demo-beat-desc">{b.desc}</p>
            </div>
          </div>
        ))}
      </Reveal>
    </Section>
  );
}
