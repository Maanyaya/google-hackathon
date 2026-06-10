import { useState } from "react";
import { Section, SectionHead } from "../ui/Section";
import { Reveal, RevealGroup } from "../ui/Reveal";
import { VideoEmbed } from "../ui/VideoEmbed";

const BUILD_MCP_VIDEO = import.meta.env.VITE_MCP_SETUP_VIDEO_URL || "";

function CopyBlock({ label, text }) {
  const [copied, setCopied] = useState(false);
  async function copy() {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      /* ignore */
    }
  }
  return (
    <div className="setup-copy-block">
      <div className="setup-copy-head">
        <span className="setup-copy-label">{label}</span>
        <button type="button" className="setup-copy-btn" onClick={copy}>
          {copied ? "Copied" : "Copy"}
        </button>
      </div>
      <pre className="setup-copy-pre scrollbar-thin">{text}</pre>
    </div>
  );
}

export function Setup({ setup, loading }) {
  const s = setup;
  const judge = s?.judge_mcp;
  const arch = s?.architecture;
  const urls = s?.urls;

  const antigravityJson = judge?.antigravity_config
    ? JSON.stringify(judge.antigravity_config, null, 2)
    : "";

  const mcpSetupVideoUrl = s?.videos?.mcp_setup || BUILD_MCP_VIDEO;
  const newRepoGuideUrl = s?.videos?.new_repo_guide;

  return (
    <Section id="setup" theme="light">
      <SectionHead
        eyebrow="Setup & docs · for judges & teammates"
        title='Core architecture + <span class="grad-text">MCP credentials</span>'
        lead="Everything you need to test MoDeX: two faces, one Fivetran + BigQuery bus. Watch the MCP setup walkthrough below, then copy judge credentials — no GCP key required."
      />

      <Reveal className="setup-video-block card">
        <div className="setup-video-head">
          <span className="setup-arch-tag tone-amber">Face 1 · video</span>
          <h3 className="setup-block-title">MoDeX MCP setup in Antigravity (new repo)</h3>
          <p className="setup-block-lead">
            Step-by-step: download <code>remote_client.py</code>, configure{" "}
            <code>~/.gemini/antigravity/mcp_config.json</code>, add{" "}
            <code>.agents/modex.json</code> in your repo,
            verify MCP tools, and log your first decision.
          </p>
        </div>
        <VideoEmbed
          url={mcpSetupVideoUrl}
          title="MoDeX MCP setup in Antigravity"
          className="demo-video-wrap setup-video-wrap"
          placeholderTitle="MCP setup video — upload in progress"
          placeholderLead="Drop your recording at frontend/public/videos/mcp-setup.mp4 and rebuild, or set MODEX_MCP_SETUP_VIDEO_URL on Cloud Run (YouTube / Loom / Drive link)."
          placeholderHint={
            newRepoGuideUrl ? (
              <>
                <span className="demo-upload-badge">Written guide</span>
                <a href={newRepoGuideUrl} target="_blank" rel="noreferrer">
                  docs/NEW_REPO_MCP_SETUP.md
                </a>
              </>
            ) : null
          }
        />
      </Reveal>

      {loading && !s ? (
        <div className="dec-empty">Loading setup…</div>
      ) : (
        <>
          <RevealGroup className="setup-arch">
            {arch && (
              <>
                <div className="setup-arch-card card">
                  <span className="setup-arch-tag tone-amber">Face 1</span>
                  <h3>{arch.face1.name}</h3>
                  <p>{arch.face1.role}</p>
                  <div className="setup-arch-tools">
                    {(arch.face1.tools || []).map((t) => (
                      <code key={t}>{t}</code>
                    ))}
                  </div>
                </div>
                <div className="setup-arch-card card setup-arch-bus">
                  <span className="setup-arch-tag tone-teal">Bus</span>
                  <h3>{arch.bus.name}</h3>
                  <p>{arch.bus.role}</p>
                  <ul>
                    {(arch.bus.sources || []).map((x) => (
                      <li key={x}>{x}</li>
                    ))}
                  </ul>
                </div>
                <div className="setup-arch-card card">
                  <span className="setup-arch-tag tone-violet">Face 2</span>
                  <h3>{arch.face2.name}</h3>
                  <p>{arch.face2.role}</p>
                  <ul>
                    {(arch.face2.jobs || []).map((x) => (
                      <li key={x}>{x}</li>
                    ))}
                  </ul>
                </div>
              </>
            )}
          </RevealGroup>

          {s?.data_flow?.length > 0 && (
            <Reveal className="setup-flow card">
              <h3 className="setup-block-title">Data flow</h3>
              <ol className="setup-flow-list">
                {s.data_flow.map((step, i) => (
                  <li key={i}>{step}</li>
                ))}
              </ol>
            </Reveal>
          )}

          <Reveal className="setup-judge card">
            <h3 className="setup-block-title">Judge MCP credentials (Face 1)</h3>
            <p className="setup-block-lead">
              Use these to connect Google Antigravity to the hosted MoDeX memory API.
              Events you log appear as <strong>developer_id: judge</strong> on the dashboard.
            </p>
            <div className="setup-kv-grid">
              <div className="setup-kv">
                <span className="setup-kv-k">Service URL</span>
                <code>{urls?.service || "—"}</code>
              </div>
              <div className="setup-kv">
                <span className="setup-kv-k">API key</span>
                <code className="setup-key">
                  {judge?.api_key || (judge?.api_key_configured ? "—" : "Not configured on server")}
                </code>
              </div>
              <div className="setup-kv">
                <span className="setup-kv-k">Demo repo</span>
                <code>{judge?.demo_project_repo || "github.com/demo/api-service"}</code>
              </div>
            </div>

            {judge?.verify_curl && (
              <CopyBlock label="Verify (curl)" text={judge.verify_curl} />
            )}

            {antigravityJson && (
              <CopyBlock
                label="Antigravity ~/.gemini/antigravity/mcp_config.json (set absolute path to remote_client.py)"
                text={antigravityJson}
              />
            )}

            {judge?.install_steps?.length > 0 && (
              <div className="setup-steps">
                <h4>Install steps</h4>
                <ol>
                  {judge.install_steps.map((step, i) => (
                    <li key={i}>{step}</li>
                  ))}
                </ol>
              </div>
            )}

            <div className="setup-links">
              {urls?.github_repo && (
                <a href={urls.github_repo} target="_blank" rel="noreferrer" className="setup-link">
                  GitHub repo
                </a>
              )}
              {urls?.remote_client_raw && (
                <a href={urls.remote_client_raw} target="_blank" rel="noreferrer" className="setup-link">
                  Download remote_client.py
                </a>
              )}
              <a
                href={`${urls?.github_repo || ""}/blob/main/JUDGES.md`}
                target="_blank"
                rel="noreferrer"
                className="setup-link"
              >
                JUDGES.md (full guide)
              </a>
              <a
                href={`${urls?.github_repo || ""}/blob/main/modex_mcp/README.md`}
                target="_blank"
                rel="noreferrer"
                className="setup-link"
              >
                MCP README
              </a>
            </div>
          </Reveal>
        </>
      )}
    </Section>
  );
}
