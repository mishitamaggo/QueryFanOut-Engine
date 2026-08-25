#!/usr/bin/env python3
"""
Query Fan-Out Engine
-------------------
Expands and decomposes a user prompt/query into targeted, multidimensional sub-queries
optimized for retrieval (RAG), search engines, and multi-agent synthesis using OpenRouter.

Author: Antigravity
"""

import os
import sys
import json
import urllib.request
import urllib.error
import argparse
from typing import List, Dict, Any, Optional

# Ensure UTF-8 output in Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Default configuration
DEFAULT_API_KEY = os.environ.get(
    "OPENROUTER_API_KEY",
    "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"
)
DEFAULT_MODEL = os.environ.get("OPENROUTER_MODEL", "openai/gpt-4o-mini")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


# Fan-out strategy system prompt definitions
SYSTEM_PROMPT = """You are an expert Query Fan-Out and Information Retrieval Specialist.
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
      "search_type": "semantic" | "lexical_keyword" | "factual",
      "priority": "high" | "medium" | "low"
    }
  ]
}
Do NOT wrap the JSON in markdown code blocks like ```json ... ``` or add extra conversational text. Return raw JSON only."""


class QueryFanOut:
    """Query Fan-Out Engine powered by OpenRouter API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        app_name: str = "QueryFanOutEngine",
        site_url: str = "https://localhost"
    ):
        self.api_key = api_key or DEFAULT_API_KEY
        if not self.api_key:
            raise ValueError(
                "API key is missing! Please provide it or set the OPENROUTER_API_KEY environment variable."
            )
        self.model = model
        self.app_name = app_name
        self.site_url = site_url

    def generate_fan_out(
        self,
        prompt: str,
        num_queries: int = 5,
        strategies: Optional[List[str]] = None,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate fanned-out sub-queries for a given prompt.

        Args:
            prompt: The original user prompt or query.
            num_queries: Target number of fanned-out queries (approximate).
            strategies: Optional filter of strategies to focus on.
            context: Optional domain context or background info.

        Returns:
            Dict containing the analysis and list of fanned-out queries.
        """
        user_message_parts = [
            f"User Prompt: \"{prompt}\"",
            f"Target Number of Fanned-Out Queries: {num_queries}"
        ]

        if strategies:
            user_message_parts.append(f"Focus especially on these strategies: {', '.join(strategies)}")

        if context:
            user_message_parts.append(f"Domain Context / Background: {context}")

        user_message = "\n".join(user_message_parts)

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.3,  # Controlled temperature for structured consistency
            "response_format": {"type": "json_object"}
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.site_url,
            "X-Title": self.app_name,
            "User-Agent": "QueryFanOut/1.0"
        }

        req = urllib.request.Request(
            OPENROUTER_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                status_code = response.getcode()
                response_data = response.read().decode("utf-8")
                
                if status_code != 200:
                    raise RuntimeError(f"OpenRouter API Error (Status {status_code}): {response_data}")

                parsed_response = json.loads(response_data)
                choice_text = parsed_response["choices"][0]["message"]["content"].strip()

                # Clean any stray markdown formatting if present
                if choice_text.startswith("```"):
                    choice_text = choice_text.split("\n", 1)[1]
                    if choice_text.endswith("```"):
                        choice_text = choice_text.rsplit("\n", 1)[0]
                    choice_text = choice_text.strip()

                result = json.loads(choice_text)
                return result

        except urllib.error.HTTPError as e:
            err_msg = e.read().decode("utf-8") if e.fp else str(e)
            raise RuntimeError(f"HTTP Error {e.code}: {err_msg}")
        except urllib.error.URLError as e:
            raise RuntimeError(f"Network Connection Error: {e.reason}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse JSON response from LLM: {choice_text}\nError: {e}")


def display_results(result: Dict[str, Any]):
    """Pretty prints the Query Fan-Out results to the terminal."""
    original = result.get("original_prompt", "N/A")
    analysis = result.get("analysis", {})
    queries = result.get("fanned_queries", [])

    print("\n" + "=" * 80)
    print(" 🚀 QUERY FAN-OUT RESULTS")
    print("=" * 80)
    print(f"📌 Original Prompt: \"{original}\"")
    print(f"🎯 Detected Intent: {analysis.get('intent', 'N/A')}")
    print(f"📊 Query Complexity: {analysis.get('complexity', 'N/A').upper()}")
    
    dimensions = analysis.get("identified_dimensions", [])
    if dimensions:
        print(f"🔍 Identified Dimensions: {', '.join(dimensions)}")
    
    print("\n" + "-" * 80)
    print(f"📋 Generated Fanned-Out Queries ({len(queries)} total):")
    print("-" * 80)

    category_emojis = {
        "decomposition": "🧩 [Decomposition]",
        "perspective": "🔭 [Perspective]",
        "keyword_variant": "🏷️  [Keywords]",
        "verification": "🛡️  [Verification]",
        "edge_case": "⚠️  [Edge Case]"
    }

    priority_badges = {
        "high": "🔴 HIGH",
        "medium": "🟡 MED",
        "low": "🟢 LOW"
    }

    for idx, q in enumerate(queries, 1):
        cat = category_emojis.get(q.get("category", ""), f"[{q.get('category', '')}]")
        prio = priority_badges.get(q.get("priority", "medium"), q.get("priority", "MED"))
        stype = q.get("search_type", "semantic")
        
        print(f"\n  #{idx} {cat} | Priority: {prio} | Type: {stype}")
        print(f"     🔎 Query: \"{q.get('query')}\"")
        print(f"     🎯 Aspect: {q.get('targeted_aspect')}")
        print(f"     💡 Rationale: {q.get('rationale')}")

    print("\n" + "=" * 80 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Query Fan-Out Tool: Decomposes and expands LLM prompts into targeted sub-queries."
    )
    parser.add_argument(
        "-p", "--prompt",
        type=str,
        help="The prompt or question to fan out."
    )
    parser.add_argument(
        "-n", "--num-queries",
        type=int,
        default=5,
        help="Approximate number of fanned-out queries to generate (default: 5)."
    )
    parser.add_argument(
        "-m", "--model",
        type=str,
        default=DEFAULT_MODEL,
        help=f"OpenRouter model to use (default: {DEFAULT_MODEL})."
    )
    parser.add_argument(
        "-k", "--api-key",
        type=str,
        default=DEFAULT_API_KEY,
        help="OpenRouter API key."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON instead of formatted text."
    )
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Run in interactive prompt mode."
    )

    args = parser.parse_args()

    engine = QueryFanOut(api_key=args.api_key, model=args.model)

    if args.interactive:
        print("\n" + "=" * 60)
        print("🌟 Query Fan-Out Interactive Console")
        print(f"Using Model: {args.model}")
        print("Type 'exit' or 'quit' to end.")
        print("=" * 60)

        while True:
            try:
                prompt_input = input("\nEnter your prompt/query: ").strip()
                if not prompt_input:
                    continue
                if prompt_input.lower() in ("exit", "quit"):
                    print("Goodbye!")
                    break

                num_input = input(f"Number of fanned queries (default {args.num_queries}): ").strip()
                num_q = int(num_input) if num_input.isdigit() else args.num_queries

                print("\n⏳ Generating fanned-out sub-queries via OpenRouter...")
                results = engine.generate_fan_out(prompt_input, num_queries=num_q)
                
                if args.json:
                    print(json.dumps(results, indent=2))
                else:
                    display_results(results)

            except KeyboardInterrupt:
                print("\nSession interrupted. Exiting...")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
    else:
        # Single execution
        target_prompt = args.prompt or "How do I build a production-ready real-time RAG pipeline with high throughput and low latency?"
        
        if not args.json:
            print(f"⏳ Generating fanned-out sub-queries for:\n\"{target_prompt}\"")
            print(f"Model: {args.model}\n")

        try:
            results = engine.generate_fan_out(target_prompt, num_queries=args.num_queries)
            if args.json:
                print(json.dumps(results, indent=2))
            else:
                display_results(results)
        except Exception as e:
            print(f"\n❌ Error: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
