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
import re
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
      "search_type": "semantic" | "lexical_keyword" | "hybrid",
      "priority": "high" | "medium" | "low"
    }
  ]
}
Do NOT wrap your JSON in conversational intro/outro text. Return raw JSON only."""


class QueryFanOut:
    """Core Query Fan-Out engine interface."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        site_url: str = "http://localhost:5000",
        app_name: str = "QueryFanOutEngine"
    ):
        self.api_key = api_key or DEFAULT_API_KEY
        self.model = model or DEFAULT_MODEL
        self.site_url = site_url
        self.app_name = app_name

    def _clean_and_parse_json(self, raw_text: str) -> Dict[str, Any]:
        """Resilient JSON parser that handles code blocks, unescaped quotes, and text preamble."""
        text = raw_text.strip()

        # Strip markdown code fences if present
        if text.startswith("```"):
            lines = text.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()

        # 1. Direct JSON parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 2. Extract outermost JSON object if enclosed in conversational text
        match = re.search(r"(\{.*\})", text, re.DOTALL)
        if match:
            extracted = match.group(1).strip()
            try:
                return json.loads(extracted)
            except json.JSONDecodeError:
                text = extracted

        # 3. Line-by-line quote fixer for inner quotes in values
        fixed_lines = []
        for line in text.splitlines():
            m = re.match(r'^(\s*"[a-zA-Z0-9_]+":\s*")(.*)("(?:\s*,\s*|\s*|\s*\}\s*))$', line)
            if m:
                prefix, val, suffix = m.group(1), m.group(2), m.group(3)
                val_escaped = re.sub(r'(?<!\\)"', r'\"', val)
                fixed_lines.append(prefix + val_escaped + suffix)
            else:
                fixed_lines.append(line)
        
        fixed_text = "\n".join(fixed_lines)
        return json.loads(fixed_text)

    def _execute_api_call(self, model: str, user_message: str) -> Dict[str, Any]:
        """Executes a single API call to OpenRouter with the given model."""
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.3,
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

        with urllib.request.urlopen(req, timeout=45) as response:
            status_code = response.getcode()
            response_data = response.read().decode("utf-8")
            
            if status_code != 200:
                raise RuntimeError(f"OpenRouter API Error (Status {status_code}): {response_data}")

            parsed_response = json.loads(response_data)
            choice_text = parsed_response["choices"][0]["message"]["content"].strip()
            return self._clean_and_parse_json(choice_text)

    def generate_fan_out(
        self,
        prompt: str,
        num_queries: int = 5,
        strategies: Optional[List[str]] = None,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Decomposes and fans out a single prompt into multidimensional sub-queries.
        Includes automatic fallback to default model if the requested model endpoint is unavailable.
        """
        user_message_parts = [
            f'User Prompt: "{prompt}"',
            f"Target Number of Fanned-Out Queries: {num_queries}"
        ]

        if strategies:
            user_message_parts.append(f"Focus especially on these strategies: {', '.join(strategies)}")

        if context:
            user_message_parts.append(f"Domain Context / Background: {context}")

        user_message = "\n".join(user_message_parts)

        target_model = self.model
        fallback_happened = False
        error_reason = ""

        try:
            result = self._execute_api_call(target_model, user_message)
        except Exception as primary_err:
            # If target model fails (e.g. 404, rate limit, parse error) and isn't default model, fallback
            if target_model != DEFAULT_MODEL:
                try:
                    result = self._execute_api_call(DEFAULT_MODEL, user_message)
                    fallback_happened = True
                    target_model = DEFAULT_MODEL
                    error_reason = str(primary_err)
                except Exception as fallback_err:
                    raise RuntimeError(f"Model {self.model} failed ({primary_err}), and fallback {DEFAULT_MODEL} failed: {fallback_err}")
            else:
                raise primary_err

        # Ensure original prompt is present
        if "original_prompt" not in result:
            result["original_prompt"] = prompt

        if "analysis" not in result or not isinstance(result["analysis"], dict):
            result["analysis"] = {
                "intent": "Decomposed query analysis",
                "complexity": "medium",
                "identified_dimensions": ["decomposition", "perspective"]
            }

        result["analysis"]["model_used"] = target_model
        if fallback_happened:
            result["analysis"]["fallback_triggered"] = True
            result["analysis"]["requested_model"] = self.model
            result["analysis"]["fallback_reason"] = error_reason

        return result


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
