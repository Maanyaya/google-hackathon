/**
 * DemoVideo — a prominent section where the demo video lives.
 * Shows a styled video embed placeholder; swap DEMO_VIDEO_URL for the real link.
 */
import { Section, SectionHead } from "../ui/Section";
import { Reveal } from "../ui/Reveal";

/** Set this env var at build time or replace the string directly. */
const DEMO_VIDEO_URL = import.meta.env.VITE_DEMO_VIDEO_URL || "";

function PlayIcon() {
  return (
    <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
      <circle cx="32" cy="32" r="31" stroke="currentColor" strokeWidth="1.5" opacity="0.3" />
      <circle cx="32" cy="32" r="24" stroke="currentColor" strokeWidth="1.5" opacity="0.5" />
      <path d="M26 20l20 12-20 12V20z" fill="currentColor" />
    </svg>
  );
}

export function DemoVideo() {
  const isYoutube = DEMO_VIDEO_URL.includes("youtube") || DEMO_VIDEO_URL.includes("youtu.be");
  const isDrive   = DEMO_VIDEO_URL.includes("drive.google");
  const isLoom    = DEMO_VIDEO_URL.includes("loom.com");

  /* normalise YouTube share links to embed format */
  let embedUrl = DEMO_VIDEO_URL;
  if (isYoutube && DEMO_VIDEO_URL) {
    const ytId = DEMO_VIDEO_URL.match(/(?:v=|youtu\.be\/)([^&?/]+)/)?.[1];
    if (ytId) embedUrl = `https://www.youtube.com/embed/${ytId}?rel=0&modestbranding=1`;
  }
  if (isDrive && DEMO_VIDEO_URL) {
    const fileId = DEMO_VIDEO_URL.match(/\/d\/([^/]+)/)?.[1];
    if (fileId) embedUrl = `https://drive.google.com/file/d/${fileId}/preview`;
  }
  if (isLoom && DEMO_VIDEO_URL) {
    embedUrl = DEMO_VIDEO_URL.replace("share", "embed");
  }

  const hasVideo = !!DEMO_VIDEO_URL;

  return (
    <Section id="demo" theme="dark" aurora>
      <SectionHead
        eyebrow="Demo · see MoDeX in action"
        title={`Watch the <span class="grad-text">agent-to-agent handoff</span>`}
        lead="Agent A captures context in Cursor. Agent B loads it in Antigravity on a different machine — with zero cold start. This is the full story in under 3 minutes."
      />

      <Reveal className="demo-video-wrap">
        {hasVideo ? (
          isYoutube || isDrive || isLoom ? (
            <div className="demo-video-frame">
              <iframe
                src={embedUrl}
                title="MoDeX demo"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
                loading="lazy"
              />
            </div>
          ) : (
            <div className="demo-video-frame">
              {/* eslint-disable-next-line jsx-a11y/media-has-caption */}
              <video src={DEMO_VIDEO_URL} controls preload="metadata" />
            </div>
          )
        ) : (
          /* placeholder — shown until VITE_DEMO_VIDEO_URL is set */
          <div className="demo-video-placeholder">
            <div className="demo-play-ring">
              <PlayIcon />
            </div>
            <div className="demo-placeholder-copy">
              <h3>Demo video coming soon</h3>
              <p>
                Set <code>VITE_DEMO_VIDEO_URL</code> to a YouTube, Google Drive, Loom, or
                direct video URL to embed it here.
              </p>
              <div className="demo-upload-hint">
                <span className="demo-upload-badge">Upload target</span>
                Upload to Google Drive / YouTube → paste the share URL as{" "}
                <code>VITE_DEMO_VIDEO_URL</code> → rebuild frontend.
              </div>
            </div>
          </div>
        )}
      </Reveal>

      {/* story beats below the video */}
      <Reveal className="demo-story-beats">
        {[
          {
            t: "0:00",
            label: "Agent A starts",
            desc: "Developer opens Cursor. Session hooks fire. Every prompt and edit is captured automatically.",
          },
          {
            t: "1:00",
            label: "Context compressed",
            desc: "Session ends. context_compressed row written to BigQuery + Google Sheet. session_summary paragraph appears in column O.",
          },
          {
            t: "1:45",
            label: "Fivetran syncs",
            desc: "stowed_register connector runs. modex_logs.modex_logs in BigQuery now has the full briefing.",
          },
          {
            t: "2:15",
            label: "Agent B hydrates",
            desc: "Different machine. Agent B calls load_context(). Receives exact decisions, rejected approaches, and last user ask. Zero cold start.",
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
