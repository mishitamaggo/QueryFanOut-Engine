"use client";

import { useState, useEffect } from "react";
import { 
  Zap, 
  Sparkles, 
  Copy, 
  Check, 
  Code2, 
  AlertTriangle, 
  Layers, 
  Sliders, 
  ArrowRight,
  RefreshCw,
  Search
} from "lucide-react";

const SAMPLE_PRESETS = [
  {
    label: "Diamond Ring Size Comparison",
    prompt: "which diamond ring will look biggest on me"
  },
  {
    label: "PostgreSQL vs MongoDB for IoT",
    prompt: "What are the key trade-offs between PostgreSQL and MongoDB for high write IoT workloads?"
  },
  {
    label: "Real-time RAG Architecture",
    prompt: "How do I build a production-ready real-time RAG pipeline with high throughput and low latency?"
  },
  {
    label: "Next.js 14 Authentication",
    prompt: "How do I implement secure JWT and session auth in Next.js 14 App Router?"
  },
  {
    label: "Kubernetes Security",
    prompt: "How do I secure an enterprise Kubernetes cluster against supply chain attacks?"
  }
];

const MODEL_OPTIONS = [
  { id: "openai/gpt-4o-mini", name: "OpenAI: GPT-4o Mini (Ultra Fast & Recommended)" },
  { id: "deepseek/deepseek-chat", name: "DeepSeek: Chat V3 (High Quality)" },
  { id: "meta-llama/llama-3.3-70b-instruct", name: "Meta: Llama 3.3 70B Instruct" },
  { id: "mistralai/mistral-small-24b-instruct-2501", name: "Mistral: Small 24B Instruct" },
  { id: "anthropic/claude-3-haiku", name: "Anthropic: Claude 3 Haiku" }
];

const CATEGORY_NAMES = {
  decomposition: "Core Sub-Problem",
  perspective: "Alternative Perspective",
  keyword_variant: "Keyword Variant",
  verification: "Prerequisite Check",
  edge_case: "Edge Case & Limits"
};

export default function Home() {
  const [prompt, setPrompt] = useState(
    "which diamond ring will look biggest on me"
  );
  const [model, setModel] = useState("openai/gpt-4o-mini");
  const [numQueries, setNumQueries] = useState(5);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [showJson, setShowJson] = useState(false);
  const [copiedId, setCopiedId] = useState(null);
  const [copiedAll, setCopiedAll] = useState(false);

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    if (!prompt.trim() || loading) return;

    setError(null);
    setLoading(true);

    try {
      const response = await fetch("/api/fanout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, model, numQueries })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to decompose query.");
      }

      setResult(data);
    } catch (err) {
      setError(err.message || "An error occurred while generating queries.");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
      handleSubmit();
    }
  };

  const handleCopySingle = (id, text) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 1600);
  };

  const handleCopyAll = () => {
    if (!result?.fanned_queries) return;
    const formatted = result.fanned_queries
      .map((q, i) => `${i + 1}. [${(q.category || "").toUpperCase()}] ${q.query}`)
      .join("\n");
    navigator.clipboard.writeText(formatted);
    setCopiedAll(true);
    setTimeout(() => setCopiedAll(false), 1600);
  };

  const retryWithDefault = () => {
    setModel("openai/gpt-4o-mini");
    setError(null);
    setTimeout(() => handleSubmit(), 50);
  };

  return (
    <>
      <header>
        <div className="header-inner">
          <div className="brand-group">
            <div className="brand-mark">
              <Zap size={18} color="#ffffff" />
            </div>
            <div className="brand-title">
              Query Fan-Out <span>Studio</span>
            </div>
          </div>
          <div className="header-badge">
            <span className="status-dot"></span>
            Next.js Engine • Active
          </div>
        </div>
      </header>

      <main className="app-container">
        <section className="hero-section">
          <div className="hero-eyebrow">
            <Sparkles size={13} />
            Autonomous Multi-Hop Expansion
          </div>
          <h1 className="hero-heading">
            Decompose complex prompts into <span>targeted sub-queries</span>.
          </h1>
          <p className="hero-description">
            Break ambiguous user questions across 5 retrieval dimensions to eliminate vocabulary mismatch and capture hidden perspectives.
          </p>
        </section>

        {/* Workspace Input Card */}
        <div className="workspace-card">
          <div className="field-label-row">
            <label htmlFor="promptInput" className="field-label">
              Original Prompt or Question
            </label>
            <span className="field-hint">Press Ctrl + Enter to run</span>
          </div>

          <textarea
            id="promptInput"
            className="prompt-textarea"
            rows={3}
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type any multifaceted question or topic..."
          />

          {/* Presets */}
          <div className="presets-group">
            <div className="presets-title">Sample Prompts</div>
            <div className="presets-grid">
              {SAMPLE_PRESETS.map((p, idx) => (
                <button
                  key={idx}
                  type="button"
                  className="preset-chip"
                  onClick={() => {
                    setPrompt(p.prompt);
                    setError(null);
                  }}
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>

          {/* Controls */}
          <div className="controls-row">
            <div className="control-item">
              <label htmlFor="modelSelect" className="field-label">
                Choose Model
              </label>
              <select
                id="modelSelect"
                className="select-input"
                value={model}
                onChange={(e) => setModel(e.target.value)}
              >
                {MODEL_OPTIONS.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="control-item">
              <div className="slider-header">
                <label htmlFor="numQueries" className="field-label">
                  Sub-queries
                </label>
                <span className="slider-badge">{numQueries}</span>
              </div>
              <input
                type="range"
                id="numQueries"
                className="range-input"
                min={3}
                max={8}
                value={numQueries}
                onChange={(e) => setNumQueries(parseInt(e.target.value, 10))}
              />
            </div>

            <button
              type="button"
              className="btn-primary"
              disabled={loading || !prompt.trim()}
              onClick={handleSubmit}
            >
              {loading ? (
                <>
                  <RefreshCw size={16} className="spinner" style={{ width: 16, height: 16, margin: 0 }} />
                  <span>Analyzing...</span>
                </>
              ) : (
                <>
                  <Zap size={16} />
                  <span>Fan-Out Query</span>
                </>
              )}
            </button>
          </div>

          {/* Error Banner */}
          {error && (
            <div className="error-banner">
              <div className="error-header">
                <AlertTriangle size={16} />
                <span>Notice: Query Generation Error</span>
              </div>
              <div className="error-msg">{error}</div>
              <div style={{ marginTop: "0.75rem" }}>
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={retryWithDefault}
                >
                  <RefreshCw size={13} />
                  Retry with GPT-4o Mini
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Loading Spinner Area */}
        {loading && (
          <div className="loading-area">
            <div className="spinner"></div>
            <div style={{ fontWeight: 600, color: "var(--text-heading)", marginBottom: "0.3rem" }}>
              Decomposing into multidimensional retrieval vectors...
            </div>
            <div style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>
              Extracting perspectives, keywords, prerequisites, and edge cases
            </div>
          </div>
        )}

        {/* Results Presentation */}
        {result && !loading && (
          <div>
            {/* Analysis Summary */}
            <div className="summary-bar">
              <div>
                <div className="summary-item-label">Detected Intent</div>
                <div className="summary-item-val">
                  {result.analysis?.intent || "Decomposed Query"}
                </div>
                {result.analysis?.fallback_triggered && (
                  <div className="fallback-indicator">
                    <Sparkles size={12} />
                    Auto-switched to GPT-4o Mini (requested endpoint was unavailable)
                  </div>
                )}
              </div>

              <div>
                <div className="summary-item-label">Query Complexity</div>
                <span
                  className={`complexity-tag complexity-${(
                    result.analysis?.complexity || "medium"
                  ).toLowerCase()}`}
                >
                  {(result.analysis?.complexity || "medium").toUpperCase()}
                </span>
              </div>

              <div>
                <div className="summary-item-label">Sub-Queries</div>
                <div className="summary-item-val" style={{ color: "var(--orange-primary)" }}>
                  {result.fanned_queries?.length || 0} Generated
                </div>
              </div>
            </div>

            {/* Results Action Bar */}
            <div className="results-header">
              <h2 className="results-title">Fanned-Out Sub-Queries</h2>
              <div style={{ display: "flex", gap: "0.6rem" }}>
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={() => setShowJson(!showJson)}
                >
                  <Code2 size={14} />
                  {showJson ? "Hide JSON" : "View JSON"}
                </button>
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={handleCopyAll}
                >
                  {copiedAll ? <Check size={14} color="#22c55e" /> : <Copy size={14} />}
                  {copiedAll ? "Copied All!" : "Copy All"}
                </button>
              </div>
            </div>

            {/* JSON Drawer */}
            {showJson && (
              <div className="json-preview">
                {JSON.stringify(result, null, 2)}
              </div>
            )}

            {/* Query Cards Grid */}
            <div className="cards-grid">
              {(result.fanned_queries || []).map((q, idx) => {
                const prio = (q.priority || "medium").toLowerCase();
                const isCopied = copiedId === (q.id || idx);

                return (
                  <div key={q.id || idx} className="query-card">
                    <div>
                      <div className="card-top">
                        <span className="category-tag">
                          {CATEGORY_NAMES[q.category] || q.category}
                        </span>
                        <span className={`priority-tag priority-${prio}`}>
                          Priority: {prio.toUpperCase()}
                        </span>
                      </div>

                      <div className="query-text">"{q.query}"</div>
                      <div className="aspect-text">{q.targeted_aspect}</div>

                      <div className="rationale-box">
                        <strong>Rationale:</strong> {q.rationale}
                      </div>
                    </div>

                    <div className="card-footer">
                      <span className="search-mode">
                        {q.search_type || "semantic"} search
                      </span>
                      <button
                        type="button"
                        className={`btn-card-copy ${isCopied ? "copied" : ""}`}
                        onClick={() => handleCopySingle(q.id || idx, q.query)}
                      >
                        {isCopied ? "Copied ✓" : "Copy"}
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </main>

      <footer>
        <p>
          <strong>Query Fan-Out Studio</strong> • Next.js & OpenRouter Engine
        </p>
      </footer>
    </>
  );
}
