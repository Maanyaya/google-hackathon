/** Normalize raw LLM text before markdown render. */

function unwrapQuotes(text) {
  let t = text.trim();
  while (
    (t.startsWith('"') && t.endsWith('"')) ||
    (t.startsWith("'") && t.endsWith("'")) ||
    (t.startsWith("“") && t.endsWith("”"))
  ) {
    t = t.slice(1, -1).trim();
  }
  return t;
}

function isJsonBlob(text) {
  const t = text.trim();
  if (!t) return true;
  if ((t.startsWith("{") && t.endsWith("}")) || (t.startsWith("[") && t.endsWith("]"))) {
    try {
      JSON.parse(t);
      return true;
    } catch {
      /* not valid JSON — keep if it reads like prose */
    }
  }
  const symbols = (t.match(/[{[\]}":]/g) || []).length;
  return t.length > 80 && symbols / t.length > 0.12 && !/\n##|\n- |\*\*/.test(t);
}

function isDelegation(text) {
  const t = text.trim();
  if (!t || t.length < 20) return true;
  return /^(I'll|I will|Let me|Routing|Delegating|Transferring|Handing off)/i.test(t);
}

/**
 * @param {string} raw
 * @returns {string}
 */
export function formatAgentAnswer(raw) {
  if (!raw) return "";

  let text = String(raw)
    .replace(/\\"/g, '"')
    .replace(/\\'/g, "'")
    .replace(/\\n/g, "\n")
    .replace(/\r\n/g, "\n");

  text = unwrapQuotes(text);

  // Drop orphan quote-only lines and stray escaped artifacts.
  text = text
    .split("\n")
    .filter((line) => !/^["'`]{1,3}$/.test(line.trim()))
    .join("\n");

  text = text.replace(/^\s*"\s*$/gm, "");
  text = text.replace(/\n{3,}/g, "\n\n").trim();

  return text;
}

/**
 * Pick the best user-facing reply from parsed event texts.
 * @param {Array<{authorId:string, text:string}>} texts
 * @returns {string}
 */
export function pickBestAnswer(texts) {
  const usable = (texts || []).filter((t) => t.text && !isJsonBlob(t.text) && !isDelegation(t.text));
  if (!usable.length) {
    const fallback = (texts || []).map((t) => t.text).filter(Boolean);
    return formatAgentAnswer(fallback.join("\n\n"));
  }

  const specialistOrder = ["memory_agent", "pipeline_agent", "action_agent"];
  for (const id of specialistOrder) {
    const fromAgent = usable.filter((t) => t.authorId === id);
    if (fromAgent.length) {
      return formatAgentAnswer(fromAgent[fromAgent.length - 1].text);
    }
  }

  return formatAgentAnswer(usable[usable.length - 1].text);
}
