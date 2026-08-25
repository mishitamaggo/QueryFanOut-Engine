#!/usr/bin/env python3
"""
End-to-End Query Fan-Out + Parallel RAG Synthesis Example
--------------------------------------------------------
Demonstrates how to use Query Fan-Out in an agentic RAG pipeline:
1. Fan out user prompt into multi-angle sub-queries.
2. Dispatch sub-queries to retrieval / search in parallel.
3. Consolidate and deduplicate retrieved knowledge snippets.
4. Synthesize a comprehensive final response.

Author: Antigravity
"""

import sys
import os
import json
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from query_fan_out import QueryFanOut, DEFAULT_API_KEY, DEFAULT_MODEL, OPENROUTER_URL

# Ensure UTF-8 output in Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def simulate_retrieval(sub_query: dict) -> dict:
    """
    Simulates retrieval from a Vector Database or Search Engine (e.g. Pinecone, Tavily, Weaviate).
    In a real app, replace this with your actual vector database query or search API call.
    """
    query_text = sub_query["query"]
    category = sub_query["category"]
    
    # Mocking retrieved knowledge passages
    mock_passage = f"[Retrieved Chunk for '{query_text}'] -> Knowledge addressing {sub_query['targeted_aspect']} from perspective of {category}."
    
    return {
        "query_id": sub_query["id"],
        "query": query_text,
        "category": category,
        "retrieved_content": mock_passage
    }


def synthesize_final_answer(prompt: str, retrieved_docs: list, api_key: str, model: str) -> str:
    """Uses LLM to synthesize the retrieved fanned-out documents into a unified response."""
    docs_formatted = "\n\n".join([
        f"--- Source #{doc['query_id']} ({doc['category']}) ---\n"
        f"Query: {doc['query']}\n"
        f"Findings: {doc['retrieved_content']}"
        for doc in retrieved_docs
    ])

    synthesis_prompt = f"""You are an advanced AI synthesizing research from a Multi-Query Fan-Out retrieval process.

User's Original Question:
"{prompt}"

Information retrieved across all fanned-out sub-queries:
{docs_formatted}

Please provide a structured, thorough, and insightful final answer that integrates all the perspectives above."""

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are an expert research synthesizer."},
            {"role": "user", "content": synthesis_prompt}
        ],
        "temperature": 0.5
    }

    req = urllib.request.Request(
        OPENROUTER_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=60) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        return res["choices"][0]["message"]["content"].strip()


def run_pipeline(prompt: str):
    print("=" * 80)
    print("🔥 AGENTIC QUERY FAN-OUT & SYNTHESIS PIPELINE")
    print("=" * 80)
    print(f"📥 Input Prompt: \"{prompt}\"\n")

    # Step 1: Query Fan-Out
    print("👉 STEP 1: Fanning out queries using OpenRouter...")
    engine = QueryFanOut(api_key=DEFAULT_API_KEY, model=DEFAULT_MODEL)
    fan_out_res = engine.generate_fan_out(prompt, num_queries=4)
    queries = fan_out_res["fanned_queries"]

    for q in queries:
        print(f"   • [{q['category'].upper()}] {q['query']}")

    # Step 2: Parallel Retrieval
    print(f"\n👉 STEP 2: Dispatching {len(queries)} sub-queries in parallel to retrieval engine...")
    with ThreadPoolExecutor(max_workers=len(queries)) as executor:
        retrieved_results = list(executor.map(simulate_retrieval, queries))

    print("   ✓ All sub-query retrieval requests completed successfully.")

    # Step 3: Synthesis
    print("\n👉 STEP 3: Synthesizing multi-query insights into final response...")
    final_answer = synthesize_final_answer(prompt, retrieved_results, DEFAULT_API_KEY, DEFAULT_MODEL)

    print("\n" + "=" * 80)
    print("🎯 FINAL SYNTHESIZED RESPONSE:")
    print("=" * 80)
    print(final_answer)
    print("=" * 80 + "\n")


if __name__ == "__main__":
    test_prompt = sys.argv[1] if len(sys.argv) > 1 else "How do I secure an enterprise Kubernetes cluster against supply chain attacks?"
    run_pipeline(test_prompt)
