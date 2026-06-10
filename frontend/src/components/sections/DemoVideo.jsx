/**
 * DemoVideo — full MoDeX handoff story (Face 1 + Face 2).
 */
import { Section, SectionHead } from "../ui/Section";
import { Reveal } from "../ui/Reveal";
import { VideoEmbed } from "../ui/VideoEmbed";

const BUILD_URL = import.meta.env.VITE_DEMO_VIDEO_URL || "";

export function DemoVideo({ videoUrl = "" }) {
  const url = videoUrl || BUILD_URL;

  return (
    <Section id="demo" theme="dark" aurora>
      <SectionHead
        eyebrow="Demo · see MoDeX in action"
        title={`Watch the <span class="grad-text">agent-to-agent handoff</span>`}
        lead="Agent A captures context in Cursor. Agent B loads it on a different machine — with zero cold start. Face 2 answers from the same memory bus."
      />

      <Reveal>
        <VideoEmbed
          url={url}
          title="MoDeX handoff demo"
          placeholderTitle="Full handoff demo coming soon"
          placeholderLead="Set MODEX_DEMO_VIDEO_URL on Cloud Run or VITE_DEMO_VIDEO_URL at build time."
          placeholderHint={
            <>
              <span className="demo-upload-badge">Upload target</span>
              YouTube / Loom / Google Drive → env var → redeploy or rebuild.
            </>
          }
        />
      </Reveal>

      <Reveal className="demo-story-beats">
        {[
          {
            t: "0:00",
            label: "Agent A starts",
            desc: "Developer opens Cursor. MCP logs decisions and rejections as they work.",
          },
          {
            t: "1:00",
            label: "Context compressed",
            desc: "compress_context writes to BigQuery + Google Sheet. session_summary in column O.",
          },
          {
            t: "1:45",
            label: "Fivetran syncs",
            desc: "stowed_register connector runs. modex_logs.modex_logs has the full briefing.",
          },
          {
            t: "2:15",
            label: "Agent B hydrates",
            desc: "Different key, same repo. load_context() delivers decisions and rejected paths.",
          },
        ].map((b) => (
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
