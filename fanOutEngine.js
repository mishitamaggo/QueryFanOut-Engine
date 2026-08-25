/**
 * Query Fan-Out Engine (JavaScript / Next.js)
 * --------------------------------------------
 * Multi-dimensional prompt decomposition and query expansion with automated model fallback.
 */

const DEFAULT_API_KEY =
  process.env.OPENROUTER_API_KEY ||
  "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";
const DEFAULT_MODEL = process.env.OPENROUTER_MODEL || "openai/gpt-4o-mini";
const OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions";

const SYSTEM_PROMPT = `You are an expert Query Fan-Out and Information Retrieval Specialist.
Your task is to analyze an incoming prompt or question and generate a structured set of fanned-out sub-queries.

### Why Query Fan-Out is Needed:
A single user prompt is often ambiguous, multifaceted, or contains implicit assumptions. Single-query retrieval fails to capture diverse perspectives, sub-topics, edge cases, and terminology variations.

### Fan-Out Dimensions to Generate:
1. **Decomposition (Core Sub-problems)**: Break complex/multi-hop requirements into atomic, focused sub-questions.
2. **Perspective & Facet Diversification**: Target technical architecture, practical implementation, trade-offs, limitations, and benchmarks.
3. **Lexical & Keyword Variants**: Rephrase using domain-specific jargon, synonyms, and search-optimized keywords to overcome vocabulary mismatch.
4. **Foundational & Contextual Verification**: Queries to check underlying assumptions, prerequisites, or baseline definitions.
5. **Edge Cases & Counter-arguments**: Inquiries addressing failure modes, security, scalability bottlenecks, or alternative solutions.

### Output Format:
You MUST respond ONLY with a valid JSON object matching this exact schema:
{
  "original_prompt": string,
  "analysis": {
    "intent": string,
    "complexity": "low" | "medium" | "high",
    "identified_dimensions": [string]
  },
  "fanned_queries": [
    {
      "id": number,
      "query": string,
      "category": "decomposition" | "perspective" | "keyword_variant" | "verification" | "edge_case",
      "targeted_aspect": string,
      "rationale": string,
      "search_type": "semantic" | "lexical_keyword" | "hybrid",
      "priority": "high" | "medium" | "low"
    }
  ]
}
Do NOT wrap your JSON in conversational intro/outro text. Return raw JSON only.`;

/**
 * Resilient JSON parser that handles code blocks, unescaped quotes, and text preamble.
 */
export function cleanAndParseJson(rawText) {
  let text = (rawText || "").trim();

  // Strip markdown code fences
  if (text.startsWith("```")) {
    const lines = text.split("\n");
    if (lines.length > 0 && lines[0].startsWith("```")) lines.shift();
    if (lines.length > 0 && lines[lines.length - 1].startsWith("```")) lines.pop();
    text = lines.join("\n").trim();
  }

  // 1. Direct JSON parse
  try {
    return JSON.parse(text);
  } catch (e) {
    // Continue to repair
  }

  // 2. Extract outermost JSON object if enclosed in conversational text
  const match = text.match(/(\{[\s\S]*\})/);
  if (match) {
    const extracted = match[1].trim();
    try {
      return JSON.parse(extracted);
    } catch (e) {
      text = extracted;
    }
  }

  // 3. Fix unescaped inner quotes in key-value lines
  const lines = text.split("\n");
  const fixedLines = lines.map((line) => {
    const kvMatch = line.match(/^(\s*"[a-zA-Z0-9_]+":\s*")(.*)("(?:\s*,\s*|\s*|\s*\}\s*))$/);
    if (kvMatch) {
      const prefix = kvMatch[1];
      const val = kvMatch[2];
      const suffix = kvMatch[3];
      const valEscaped = val.replace(/(?<!\\)"/g, '\\"');
      return prefix + valEscaped + suffix;
    }
    return line;
  });

  const fixedText = fixedLines.join("\n");
  return JSON.parse(fixedText);
}

/**
 * Executes a single API call to OpenRouter
 */
async function callOpenRouter(model, userMessage, apiKey) {
  const response = await fetch(OPENROUTER_URL, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${apiKey}`,
      "Content-Type": "application/json",
      "HTTP-Referer": "http://localhost:3000",
      "X-Title": "QueryFanOutNextJS",
      "User-Agent": "QueryFanOutNextJS/1.0"
    },
    body: JSON.stringify({
      model: model,
      messages: [
        { role: "system", content: SYSTEM_PROMPT },
        { role: "user", content: userMessage }
      ],
      temperature: 0.3,
      response_format: { type: "json_object" }
    })
  });

  if (!response.ok) {
    const errBody = await response.text();
    throw new Error(`OpenRouter HTTP ${response.status}: ${errBody}`);
  }

  const data = await response.json();
  const rawChoice = data?.choices?.[0]?.message?.content?.trim();
  if (!rawChoice) {
    throw new Error("No response content returned from OpenRouter.");
  }

  return cleanAndParseJson(rawChoice);
}

/**
 * Generate fanned-out queries for a prompt with automatic fallback
 */
export async function generateFanOut(prompt, options = {}) {
  const apiKey = options.apiKey || DEFAULT_API_KEY;
  const requestedModel = options.model || DEFAULT_MODEL;
  const numQueries = options.numQueries || 5;
  const context = options.context || "";
  const strategies = options.strategies || [];

  if (!apiKey) {
    throw new Error("OpenRouter API key is required.");
  }

  const userMessageParts = [
    `User Prompt: "${prompt}"`,
    `Target Number of Fanned-Out Queries: ${numQueries}`
  ];

  if (strategies && strategies.length > 0) {
    userMessageParts.push(`Focus especially on these strategies: ${strategies.join(", ")}`);
  }

  if (context) {
    userMessageParts.push(`Domain Context / Background: ${context}`);
  }

  const userMessage = userMessageParts.join("\n");

  let targetModel = requestedModel;
  let fallbackHappened = false;
  let fallbackReason = "";
  let result = null;

  try {
    result = await callOpenRouter(targetModel, userMessage, apiKey);
  } catch (primaryErr) {
    // If requested model fails and isn't the default, seamlessly fall back to DEFAULT_MODEL
    if (targetModel !== DEFAULT_MODEL) {
      try {
        result = await callOpenRouter(DEFAULT_MODEL, userMessage, apiKey);
        fallbackHappened = true;
        targetModel = DEFAULT_MODEL;
        fallbackReason = primaryErr.message;
      } catch (fallbackErr) {
        throw new Error(
          `Model ${requestedModel} failed (${primaryErr.message}), and fallback ${DEFAULT_MODEL} failed: ${fallbackErr.message}`
        );
      }
    } else {
      throw primaryErr;
    }
  }

  if (!result.original_prompt) {
    result.original_prompt = prompt;
  }

  if (!result.analysis || typeof result.analysis !== "object") {
    result.analysis = {
      intent: "Decomposed query analysis",
      complexity: "medium",
      identified_dimensions: ["decomposition", "perspective"]
    };
  }

  result.analysis.model_used = targetModel;
  if (fallbackHappened) {
    result.analysis.fallback_triggered = true;
    result.analysis.requested_model = requestedModel;
    result.analysis.fallback_reason = fallbackReason;
  }

  return result;
}
