/**
 * Query Fan-Out Engine (Node.js / JavaScript ES Module)
 * ----------------------------------------------------
 * Decomposes and expands LLM prompts into multidimensional sub-queries using OpenRouter.
 */

const OPENROUTER_API_KEY =
  process.env.OPENROUTER_API_KEY ||
  "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";
const OPENROUTER_MODEL = process.env.OPENROUTER_MODEL || "openai/gpt-4o-mini";
const OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions";

const SYSTEM_PROMPT = `You are an expert Query Fan-Out and Information Retrieval Specialist.
Your task is to analyze an incoming prompt or question and generate a structured set of fanned-out sub-queries.

### Fan-Out Dimensions:
1. Decomposition (Core Sub-problems)
2. Perspective & Facet Diversification (architecture, trade-offs, benchmarks)
3. Lexical & Keyword Variants (synonyms, technical search terms)
4. Foundational & Contextual Verification (prerequisites, baseline facts)
5. Edge Cases & Counter-arguments (failure modes, security, limitations)

### Output Format:
Respond ONLY with a valid JSON object matching this schema:
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
      "search_type": "semantic" | "lexical_keyword" | "factual",
      "priority": "high" | "medium" | "low"
    }
  ]
}
Return raw JSON only without markdown codeblocks.`;

/**
 * Generate fanned-out queries for a prompt
 * @param {string} prompt - Original prompt
 * @param {object} options - Optional configuration options
 * @returns {Promise<object>} Parsed JSON response containing fanned queries
 */
export async function fanOutQuery(prompt, options = {}) {
  const apiKey = options.apiKey || OPENROUTER_API_KEY;
  const model = options.model || OPENROUTER_MODEL;
  const numQueries = options.numQueries || 5;
  const context = options.context || "";

  if (!apiKey) {
    throw new Error("OpenRouter API key is required.");
  }

  let userContent = `User Prompt: "${prompt}"\nTarget Number of Fanned-Out Queries: ${numQueries}`;
  if (context) {
    userContent += `\nDomain Context: ${context}`;
  }

  const response = await fetch(OPENROUTER_URL, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${apiKey}`,
      "Content-Type": "application/json",
      "HTTP-Referer": "https://localhost",
      "X-Title": "QueryFanOutJS"
    },
    body: JSON.stringify({
      model: model,
      messages: [
        { role: "system", content: SYSTEM_PROMPT },
        { role: "user", content: userContent }
      ],
      temperature: 0.3,
      response_format: { type: "json_object" }
    })
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`OpenRouter API Error (${response.status}): ${errorBody}`);
  }

  const data = await response.json();
  let content = data.choices[0].message.content.trim();

  // Strip markdown code block delimiters if present
  if (content.startsWith("```")) {
    content = content.replace(/^```(?:json)?\n?/, "").replace(/\n?```$/, "");
  }

  return JSON.parse(content);
}

// Direct CLI execution demo
if (import.meta.url === `file://${process.argv[1]}` || process.argv[1]?.endsWith("query_fan_out.js")) {
  const prompt = process.argv[2] || "How to optimize vector search latency in Pinecone for 10M embeddings?";
  console.log(`\n⏳ Generating fanned-out queries for:\n"${prompt}"\n`);
  
  fanOutQuery(prompt)
    .then((res) => {
      console.log("=== Query Fan-Out Results ===");
      console.log(`Intent: ${res.analysis.intent}`);
      console.log(`Complexity: ${res.analysis.complexity}`);
      console.log("\nFanned Queries:");
      res.fanned_queries.forEach((q) => {
        console.log(`\n[${q.category.toUpperCase()}] (${q.priority.toUpperCase()} Priority)`);
        console.log(`Query: "${q.query}"`);
        console.log(`Aspect: ${q.targeted_aspect}`);
        console.log(`Rationale: ${q.rationale}`);
      });
    })
    .catch((err) => {
      console.error("Error:", err.message);
      process.exit(1);
    });
}
