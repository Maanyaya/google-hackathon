import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

/**
 * Renders agent markdown with MoDeX mission-console typography.
 */
export function AgentAnswer({ content }) {
  if (!content?.trim()) {
    return <p className="mission-answer-empty">Mission completed — no text response.</p>;
  }

  return (
    <div className="agent-answer-md">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          h2: ({ children }) => <h2 className="aa-h2">{children}</h2>,
          h3: ({ children }) => <h3 className="aa-h3">{children}</h3>,
          p: ({ children }) => <p className="aa-p">{children}</p>,
          ul: ({ children }) => <ul className="aa-ul">{children}</ul>,
          ol: ({ children }) => <ol className="aa-ol">{children}</ol>,
          li: ({ children }) => <li className="aa-li">{children}</li>,
          strong: ({ children }) => <strong className="aa-strong">{children}</strong>,
          em: ({ children }) => <em className="aa-em">{children}</em>,
          code: ({ inline, children }) =>
            inline ? (
              <code className="aa-code-inline">{children}</code>
            ) : (
              <code className="aa-code-block">{children}</code>
            ),
          pre: ({ children }) => <pre className="aa-pre">{children}</pre>,
          blockquote: ({ children }) => <blockquote className="aa-quote">{children}</blockquote>,
          hr: () => <hr className="aa-hr" />,
          a: ({ href, children }) => (
            <a className="aa-link" href={href} target="_blank" rel="noreferrer">
              {children}
            </a>
          ),
          table: ({ children }) => (
            <div className="aa-table-wrap">
              <table className="aa-table">{children}</table>
            </div>
          ),
          th: ({ children }) => <th className="aa-th">{children}</th>,
          td: ({ children }) => <td className="aa-td">{children}</td>,
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
