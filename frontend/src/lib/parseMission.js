/** Parse ADK /run event stream into a demo-friendly mission result. */

const AGENT_LABELS = {
  orchestrator_agent: "Central Memory Guide",
  memory_agent: "Memory Answers",
  pipeline_agent: "Fivetran Operations",
  action_agent: "Governed Actions",
};

function label(id) {
  return AGENT_LABELS[id] || id?.replace(/_/g, " ") || "Agent";
}

/**
 * @param {Array<object>} events ADK run response
 * @returns {{ trace: Array<{step:number, agent:string, action:string}>, answer: string, toolNames: string[] }}
 */
export function parseMissionEvents(events) {
  const trace = [];
  const texts = [];
  const toolNames = [];

  for (const ev of events || []) {
    const author = ev.author || "agent";
    const parts = ev.content?.parts || [];
    const isModel = ev.content?.role === "model";

    for (const part of parts) {
      if (part.functionCall) {
        const { name, args } = part.functionCall;
        toolNames.push(name);
        if (name === "transfer_to_agent") {
          const target = args?.agent_name;
          trace.push({
            step: trace.length + 1,
            agent: label(author),
            action: `routes to ${label(target)}`,
          });
        } else {
          trace.push({
            step: trace.length + 1,
            agent: label(author),
            action: name,
          });
        }
      }
      if (part.text && isModel) {
        texts.push({ author: label(author), text: part.text.trim() });
      }
    }
  }

  // Prefer the last substantive specialist reply (usually memory/pipeline).
  const substantive = texts.filter((t) => t.text.length > 40);
  const answer =
    (substantive.length ? substantive[substantive.length - 1].text : null) ||
    texts.map((t) => t.text).join("\n\n") ||
    "";

  return { trace, answer, toolNames, texts };
}
