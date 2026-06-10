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
    sec: 0,
    label: "Meet MoDeX",
    desc: "The memory hub for AI coding agents — shared, persistent memory built on Gemini, ADK, Google Cloud, and Fivetran.",
  },
  {
    t: "0:14",
    sec: 14,
    label: "Two faces, one system",
    desc: "Face 1 captures decisions live in your IDE. Face 2 makes that shared memory accessible and manages pipelines.",
  },
  {
    t: "0:27",
    sec: 27,
    label: "The memory bus",
    desc: "Fivetran + BigQuery at the core. Everything on Google Cloud — data flows from IDE sessions into BigQuery, kept fresh by Fivetran.",
  },
  {
    t: "0:45",
    sec: 45,
    label: "Face 1 — MCP in the IDE",
    desc: "MCP loads context. Logs flow to spreadsheets — transcripts, summaries. Context compressed and stored as shared memory across tools.",
  },
  {
    t: "1:28",
    sec: 88,
    label: "Agent handoff — zero cold start",
    desc: "Antigravity agent hydrates from loaded context. New agent starts exactly where the last one left off.",
  },
  {
    t: "2:32",
    sec: 152,
    label: "Fivetran connectors → BigQuery",
    desc: "Session logs, GitHub PRs, and platform lineage sync into the warehouse. Three connectors, one unified memory bus.",
  },
  {
    t: "3:37",
    sec: 217,
    label: "Face 2 — pipeline trust (Fivetran MCP live)",
    desc: "Check pipeline health via Fivetran MCP. Not just “is data synced?” — “is it trustworthy?” That’s the partner superpower.",
  },
  {
    t: "4:02",
    sec: 242,
    label: "Try it yourself",
    desc: "Grab MCP config from GitHub — everything is live. Thank you, Team MoDeX.",
  },
];

export function DemoVideo({ videoUrl = "" }) {
  const url = DEMO_VIDEO_URL || videoUrl;

  return (
    <Section id="demo" theme="dark" aurora>
      <SectionHead
        eyebrow="Demo · see MoDeX in action"
        title={`Watch the <span class="grad-text">full demo</span>`}
        lead="Full walkthrough synced to the narration: IDE capture → agent handoff → Fivetran connectors → Face 2 pipeline trust. Timestamps below match the video."
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
          <a
            key={b.t}
            className="demo-beat demo-beat-link"
            href={`${DEMO_VIDEO_URL}?t=${b.sec}`}
            target="_blank"
            rel="noreferrer"
            title={`Jump to ${b.t} in demo video`}
          >
            <span className="demo-beat-t">{b.t}</span>
            <div>
              <strong className="demo-beat-label">{b.label}</strong>
              <p className="demo-beat-desc">{b.desc}</p>
            </div>
          </a>
        ))}
      </Reveal>
    </Section>
  );
}
