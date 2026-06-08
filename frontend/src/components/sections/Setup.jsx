import { useState } from "react";
import { Section, SectionHead } from "../ui/Section";
import { Reveal, RevealGroup } from "../ui/Reveal";

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

  const cursorJson = judge?.cursor_config
    ? JSON.stringify(judge.cursor_config, null, 2)
    : "";

  return (
    <Section id="setup" theme="light">
      <SectionHead
        eyebrow="Setup & docs · for judges & teammates"
        title='Core architecture + <span class="grad-text">MCP credentials</span>'
        lead="Everything you need to test MoDeX: two faces, one Fivetran + BigQuery bus. Face 1 MCP credentials are below — no GCP key required. Full guide also in JUDGES.md on GitHub."
      />

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
              Use these to connect Cursor or Antigravity to the hosted MoDeX memory API.
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

            {cursorJson && (
              <CopyBlock
                label="Cursor ~/.cursor/mcp.json (set absolute path to remote_client.py)"
                text={cursorJson}
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
