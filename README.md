# ⚡ Query Fan-Out Engine

A multi-dimensional **Query Fan-Out Engine** built on OpenRouter. It decomposes, expands, and diversifies complex LLM prompts into targeted sub-queries for Advanced RAG, Search Engines, Multi-Agent Systems, and Knowledge Graphs.

---

## 💡 Why Query Fan-Out?

Single queries often suffer from:
* **Vocabulary Mismatch**: The terminology the user uses doesn't match the indexed database documents.
* **Compound/Multi-hop Intents**: A single prompt asks questions across different systems, steps, or trade-offs.
* **Missing Assumptions**: Foundational context or edge cases are ignored.

**Query Fan-Out** solves this by decomposing a prompt across 5 key dimensions:

```
                          ┌─────────────────────────────┐
                          │    Original User Prompt     │
                          └──────────────┬──────────────┘
                                         │
                                         ▼
                            [ Query Fan-Out Engine ]
                                         │
     ┌───────────────────┬───────────────┼───────────────┬──────────────────┐
     ▼                   ▼               ▼               ▼                  ▼
🧩 Decomposition   🔭 Perspective   🏷️ Keywords    🛡️ Verification   ⚠️ Edge Cases
 (Core Sub-tasks) (Architectures)   (Synonyms)    (Prerequisites)   (Failure Modes)
     │                   │               │               │                  │
     └───────────────────┴───────────────┼───────────────┴──────────────────┘
                                         ▼
                          [ Parallel Multi-Retrieval ]
                                         ▼
                           [ Comprehensive Answer ]
```

---

## 📦 Files in this Project

| File | Description |
|---|---|
| [query_fan_out.py](file:///c:/Users/user/Downloads/QueryFanOut/query_fan_out.py) | Pure Python standard library implementation (zero extra pip dependencies needed). Supports CLI, interactive mode, and JSON export. |
| [example_rag_pipeline.py](file:///c:/Users/user/Downloads/QueryFanOut/example_rag_pipeline.py) | End-to-end example demonstrating Query Fan-Out + Parallel Retrieval + Final Synthesis. |
| [query_fan_out.js](file:///c:/Users/user/Downloads/QueryFanOut/query_fan_out.js) | Node.js / ES Module implementation using native `fetch` (compatible with Node 18+, Bun, Deno, Next.js). |
| [.env](file:///c:/Users/user/Downloads/QueryFanOut/.env) | Pre-configured environment file holding the OpenRouter API Key. |

---

## ⚡ Quick Start

### 🌐 1. Launch Interactive Local Web Studio (Recommended):
```bash
python server.py
```
Open **[http://localhost:5000](http://localhost:5000)** in your browser!

### 💻 2. Run via CLI:
```bash
python query_fan_out.py -p "What are the trade-offs between PostgreSQL and MongoDB for high write IoT workloads?" -n 5
```

### 2. Run in Interactive Mode:
```bash
python query_fan_out.py --interactive
```

### 3. Output Raw JSON:
```bash
python query_fan_out.py -p "How do I implement JWT auth in Next.js 14?" --json
```

### 4. Run the Full Parallel RAG Pipeline:
```bash
python example_rag_pipeline.py "How do I secure an enterprise Kubernetes cluster against supply chain attacks?"
```

---

## 💻 Python Code Usage

You can import `QueryFanOut` directly into your existing Python projects:

```python
from query_fan_out import QueryFanOut

# Initialize with your API key
engine = QueryFanOut(
    api_key="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",
    model="openai/gpt-4o-mini"
)

# Generate 5 fanned-out queries
result = engine.generate_fan_out(
    prompt="How can I scale real-time chat with WebSockets on AWS?",
    num_queries=5
)

# Access structured data
print("Intent:", result["analysis"]["intent"])
for item in result["fanned_queries"]:
    print(f"[{item['category']}] -> {item['query']}")
```

---

## 🌐 JavaScript / Node.js Usage

```javascript
import { fanOutQuery } from './query_fan_out.js';

const result = await fanOutQuery("How do I migrate from MySQL to DynamoDB?", {
  numQueries: 5
});

console.log(result.fanned_queries);
```

---

## 📊 Structured JSON Output Format

The engine guarantees structured JSON output adhering to this schema:

```json
{
  "original_prompt": "What are the key trade-offs between PostgreSQL and MongoDB for high write IoT workloads?",
  "analysis": {
    "intent": "Comparative analysis of databases for IoT write workloads",
    "complexity": "high",
    "identified_dimensions": [
      "Decomposition",
      "Perspective & Facet Diversification",
      "Lexical & Keyword Variants",
      "Foundational & Contextual Verification",
      "Edge Cases & Counter-arguments"
    ]
  },
  "fanned_queries": [
    {
      "id": 1,
      "query": "What are the performance benchmarks for PostgreSQL and MongoDB under high write loads?",
      "category": "decomposition",
      "targeted_aspect": "performance comparison",
      "rationale": "Breaks down direct write throughput metrics.",
      "search_type": "factual",
      "priority": "high"
    },
    {
      "id": 2,
      "query": "What are the scalability limitations of PostgreSQL and MongoDB for IoT applications?",
      "category": "perspective",
      "targeted_aspect": "scalability",
      "rationale": "Explores horizontal vs vertical scaling overhead.",
      "search_type": "factual",
      "priority": "high"
    }
  ]
}
```
