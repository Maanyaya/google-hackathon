/** Parse ADK /run event stream into a demo-friendly mission result. */

import { formatAgentAnswer, pickBestAnswer } from "./formatAgentAnswer";

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
 * @returns {{ trace: Array<{step:number, agent:string, action:string}>, answer: string, toolNames: string[], texts: Array<{authorId:string, author:string, text:string}> }}
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
        const cleaned = formatAgentAnswer(part.text);
        if (cleaned) {
          texts.push({ authorId: author, author: label(author), text: cleaned });
        }
      }
    }
  }

  const answer = pickBestAnswer(texts);

  return { trace, answer, toolNames, texts };
}
