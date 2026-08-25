#!/usr/bin/env python3
"""
Query Fan-Out Engine Web Server
------------------------------
Humanized Editorial Interface for Query Fan-Out.
Carefully balanced color palette: Warm Studio Orange (10%), Crisp White & Silver (30%), Matte Obsidian Black (60%).
Runs on http://localhost:5000 with zero external dependencies!

Author: Antigravity
"""

import sys
import os
import json
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from query_fan_out import QueryFanOut, DEFAULT_API_KEY, DEFAULT_MODEL, OPENROUTER_URL

# Ensure UTF-8 output in Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PORT = int(os.environ.get("PORT", 5000))

HTML_CONTENT = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Query Fan-Out Engine</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@500;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    /* ==========================================================================
       Humanized Design System (60% Matte Black, 30% White/Slate, 10% Studio Orange)
       ========================================================================== */
    :root {
      /* 60% Black & Deep Charcoal Base */
      --bg-canvas: #0c0d0e;
      --bg-surface: #141518;
      --bg-surface-raised: #1c1d22;
      --bg-surface-sunken: #09090b;
      --border-subtle: rgba(255, 255, 255, 0.08);
      --border-medium: rgba(255, 255, 255, 0.14);
      --border-interactive: rgba(249, 115, 22, 0.4);

      /* 30% Crisp White & Muted Titanium Typography */
      --text-heading: #fafafa;
      --text-body: #d4d4d8;
      --text-muted: #8e8e93;
      --text-faint: #52525b;

      /* 10% Studio Orange Accents (Humanized, tactile, warm) */
      --orange-primary: #f97316;
      --orange-hover: #ea580c;
      --orange-active: #c2410c;
      --orange-tint: rgba(249, 115, 22, 0.08);
      --orange-tint-medium: rgba(249, 115, 22, 0.16);
      --orange-border: rgba(249, 115, 22, 0.28);
      --orange-highlight: #fb923c;

      --radius-sm: 8px;
      --radius-md: 12px;
      --radius-lg: 18px;
      --radius-full: 9999px;
      --shadow-card: 0 4px 20px -2px rgba(0, 0, 0, 0.4), 0 2px 6px -1px rgba(0, 0, 0, 0.2);
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      background-color: var(--bg-canvas);
      color: var(--text-body);
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      line-height: 1.5;
      -webkit-font-smoothing: antialiased;
    }

    /* Subtle warm ambient lighting */
    body::before {
      content: '';
      position: fixed;
      top: 0;
      left: 50%;
      transform: translateX(-50%);
      width: 850px;
      height: 280px;
      background: radial-gradient(ellipse at center, rgba(249, 115, 22, 0.06) 0%, transparent 70%);
      pointer-events: none;
      z-index: 0;
    }

    /* Navigation Bar */
    header {
      padding: 1.25rem 2rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid var(--border-subtle);
      background: rgba(12, 13, 14, 0.9);
      backdrop-filter: blur(12px);
      position: sticky;
      top: 0;
      z-index: 50;
    }

    .brand-group {
      display: flex;
      align-items: center;
      gap: 0.85rem;
    }

    .brand-mark {
      width: 32px;
      height: 32px;
      background-color: var(--orange-primary);
      border-radius: var(--radius-sm);
      display: flex;
      align-items: center;
      justify-content: center;
      color: #ffffff;
      font-weight: 800;
      font-size: 0.95rem;
      letter-spacing: -0.5px;
    }

    .brand-title {
      font-size: 1.15rem;
      font-weight: 700;
      color: var(--text-heading);
      letter-spacing: -0.3px;
    }

    .brand-title span {
      color: var(--orange-primary);
    }

    .header-subtext {
      font-size: 0.82rem;
      color: var(--text-muted);
      font-weight: 500;
    }

    /* Main Content */
    main {
      max-width: 1040px;
      margin: 0 auto;
      padding: 3.5rem 1.5rem 5rem 1.5rem;
      width: 100%;
      flex: 1;
      position: relative;
      z-index: 1;
    }

    /* Editorial Hero */
    .hero-container {
      margin-bottom: 2.75rem;
    }

    .hero-eyebrow {
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      font-size: 0.78rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 1.2px;
      color: var(--orange-primary);
      margin-bottom: 0.85rem;
    }

    .hero-eyebrow::before {
      content: '';
      width: 6px;
      height: 6px;
      background-color: var(--orange-primary);
      border-radius: 50%;
    }

    .hero-heading {
      font-size: 2.5rem;
      font-weight: 800;
      color: var(--text-heading);
      letter-spacing: -1px;
      line-height: 1.2;
      margin-bottom: 0.85rem;
    }

    .hero-heading span {
      color: var(--orange-primary);
    }

    .hero-description {
      font-size: 1.05rem;
      color: var(--text-muted);
      max-width: 620px;
      line-height: 1.6;
    }

    /* Workspace Card */
    .workspace-card {
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-lg);
      padding: 1.75rem;
      box-shadow: var(--shadow-card);
      margin-bottom: 2.5rem;
    }

    .input-label-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.6rem;
    }

    .field-label {
      font-size: 0.82rem;
      font-weight: 600;
      color: var(--text-heading);
    }

    .field-hint {
      font-size: 0.78rem;
      color: var(--text-muted);
    }

    /* Prompt Textarea */
    textarea {
      width: 100%;
      height: 110px;
      background: var(--bg-surface-sunken);
      border: 1px solid var(--border-medium);
      border-radius: var(--radius-md);
      padding: 1rem 1.15rem;
      color: var(--text-heading);
      font-family: inherit;
      font-size: 0.98rem;
      resize: vertical;
      outline: none;
      transition: border-color 0.2s, background 0.2s;
      line-height: 1.55;
    }

    textarea:focus {
      border-color: var(--orange-primary);
      background: #0f1013;
    }

    textarea::placeholder {
      color: var(--text-faint);
    }

    /* Presets Container */
    .presets-wrapper {
      margin-top: 1rem;
      margin-bottom: 1.75rem;
    }

    .presets-title {
      font-size: 0.75rem;
      font-weight: 700;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.6px;
      margin-bottom: 0.55rem;
    }

    .presets-list {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
    }

    .preset-button {
      background: var(--bg-surface-raised);
      border: 1px solid var(--border-subtle);
      padding: 0.4rem 0.85rem;
      border-radius: var(--radius-full);
      font-size: 0.82rem;
      font-weight: 500;
      color: var(--text-body);
      cursor: pointer;
      transition: all 0.18s ease;
      user-select: none;
    }

    .preset-button:hover {
      background: var(--orange-tint);
      border-color: var(--orange-border);
      color: var(--text-heading);
    }

    /* Controls Panel */
    .controls-grid {
      display: grid;
      grid-template-columns: 1.5fr 1fr auto;
      gap: 1.25rem;
      align-items: flex-end;
      padding-top: 1.25rem;
      border-top: 1px solid var(--border-subtle);
    }

    @media (max-width: 768px) {
      .controls-grid {
        grid-template-columns: 1fr;
      }
    }

    .control-item {
      display: flex;
      flex-direction: column;
      gap: 0.45rem;
    }

    select {
      background: var(--bg-surface-sunken);
      border: 1px solid var(--border-medium);
      border-radius: var(--radius-sm);
      padding: 0.65rem 0.85rem;
      color: var(--text-heading);
      font-family: inherit;
      font-size: 0.88rem;
      outline: none;
      cursor: pointer;
      transition: border-color 0.2s;
    }

    select:focus {
      border-color: var(--orange-primary);
    }

    /* Slider styling */
    .slider-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .slider-value {
      font-weight: 700;
      color: var(--orange-primary);
      font-size: 0.9rem;
    }

    input[type="range"] {
      width: 100%;
      height: 6px;
      background: var(--bg-surface-raised);
      border-radius: var(--radius-full);
      accent-color: var(--orange-primary);
      cursor: pointer;
      margin: 0.4rem 0;
    }

    /* Primary Action Button */
    .btn-submit {
      background-color: var(--orange-primary);
      color: #ffffff;
      border: none;
      padding: 0.75rem 1.85rem;
      border-radius: var(--radius-sm);
      font-size: 0.92rem;
      font-weight: 700;
      letter-spacing: -0.2px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      transition: background-color 0.15s ease, transform 0.1s ease;
      height: 42px;
    }

    .btn-submit:hover:not(:disabled) {
      background-color: var(--orange-hover);
    }

    .btn-submit:active:not(:disabled) {
      background-color: var(--orange-active);
      transform: translateY(1px);
    }

    .btn-submit:disabled {
      opacity: 0.4;
      cursor: not-allowed;
    }

    /* Results Presentation */
    .results-wrapper {
      display: none;
      animation: slideUp 0.3s ease-out;
    }

    @keyframes slideUp {
      from { opacity: 0; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }

    /* Summary Bar */
    .summary-card {
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-left: 3px solid var(--orange-primary);
      border-radius: var(--radius-md);
      padding: 1.15rem 1.5rem;
      display: grid;
      grid-template-columns: 2fr 1fr 1fr;
      gap: 1.25rem;
      margin-bottom: 2rem;
      align-items: center;
    }

    @media (max-width: 640px) {
      .summary-card {
        grid-template-columns: 1fr;
      }
    }

    .summary-cell-label {
      font-size: 0.72rem;
      font-weight: 700;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 0.2rem;
    }

    .summary-cell-value {
      font-size: 0.95rem;
      font-weight: 600;
      color: var(--text-heading);
    }

    .complexity-pill {
      display: inline-block;
      padding: 0.2rem 0.6rem;
      border-radius: var(--radius-sm);
      font-size: 0.75rem;
      font-weight: 700;
      text-transform: uppercase;
    }

    .complexity-high { background: var(--orange-tint-medium); color: var(--orange-highlight); border: 1px solid var(--orange-border); }
    .complexity-medium { background: var(--bg-surface-raised); color: var(--text-heading); border: 1px solid var(--border-medium); }
    .complexity-low { background: var(--bg-surface-raised); color: var(--text-muted); border: 1px solid var(--border-subtle); }

    /* Results Header & Actions */
    .results-actions-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.25rem;
    }

    .results-heading {
      font-size: 1.15rem;
      font-weight: 700;
      color: var(--text-heading);
    }

    .btn-secondary {
      background: var(--bg-surface);
      border: 1px solid var(--border-medium);
      color: var(--text-body);
      padding: 0.45rem 0.95rem;
      border-radius: var(--radius-sm);
      font-size: 0.8rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s ease;
    }

    .btn-secondary:hover {
      background: var(--bg-surface-raised);
      color: var(--text-heading);
      border-color: var(--orange-primary);
    }

    /* Cards Grid */
    .cards-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(310px, 1fr));
      gap: 1.25rem;
      margin-bottom: 2rem;
    }

    .query-card {
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      padding: 1.35rem;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 1rem;
      transition: border-color 0.2s ease, transform 0.15s ease;
    }

    .query-card:hover {
      border-color: var(--border-interactive);
      transform: translateY(-2px);
    }

    .card-header-line {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .tag-category {
      font-size: 0.72rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      padding: 0.2rem 0.55rem;
      border-radius: 4px;
      background: var(--orange-tint);
      color: var(--orange-highlight);
      border: 1px solid var(--orange-border);
    }

    .tag-priority {
      font-size: 0.7rem;
      font-weight: 600;
      color: var(--text-muted);
    }

    .prio-high { color: var(--orange-primary); font-weight: 700; }

    .query-statement {
      font-size: 0.98rem;
      font-weight: 600;
      color: var(--text-heading);
      line-height: 1.45;
    }

    .target-aspect-text {
      font-size: 0.8rem;
      font-weight: 600;
      color: var(--orange-primary);
      margin-top: 0.4rem;
    }

    .rationale-box {
      background: var(--bg-surface-sunken);
      border-radius: var(--radius-sm);
      padding: 0.75rem 0.85rem;
      font-size: 0.82rem;
      color: var(--text-muted);
      line-height: 1.45;
      border: 1px solid rgba(255, 255, 255, 0.03);
    }

    .rationale-box strong {
      color: var(--text-body);
      font-weight: 600;
    }

    .card-bottom-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-top: 0.75rem;
      border-top: 1px solid var(--border-subtle);
      margin-top: auto;
    }

    .search-mode {
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.72rem;
      color: var(--text-faint);
    }

    .btn-card-copy {
      background: transparent;
      border: 1px solid var(--border-medium);
      color: var(--text-body);
      padding: 0.25rem 0.65rem;
      border-radius: 4px;
      font-size: 0.74rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s ease;
    }

    .btn-card-copy:hover {
      background: var(--orange-primary);
      border-color: var(--orange-primary);
      color: #ffffff;
    }

    /* JSON Drawer */
    .json-preview {
      display: none;
      background: var(--bg-surface-sunken);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      padding: 1.25rem;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.82rem;
      color: var(--orange-highlight);
      max-height: 380px;
      overflow-y: auto;
      white-space: pre-wrap;
      margin-bottom: 2rem;
    }

    /* Loading State */
    .loader-area {
      display: none;
      text-align: center;
      padding: 3.5rem 1rem;
    }

    .loader-wheel {
      width: 36px;
      height: 36px;
      border: 2.5px solid var(--border-medium);
      border-top-color: var(--orange-primary);
      border-radius: 50%;
      animation: rotate 0.75s linear infinite;
      margin: 0 auto 1rem auto;
    }

    @keyframes rotate {
      to { transform: rotate(360deg); }
    }

    /* Error Banner */
    .error-banner {
      display: none;
      background: rgba(239, 68, 68, 0.12);
      border: 1px solid rgba(239, 68, 68, 0.35);
      border-radius: var(--radius-md);
      padding: 1.25rem 1.5rem;
      margin: 1.5rem 0;
      color: #fecaca;
      animation: fadeIn 0.25s ease;
    }

    .error-banner-header {
      font-weight: 700;
      font-size: 0.95rem;
      color: #f87171;
      margin-bottom: 0.35rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .error-banner-msg {
      font-size: 0.85rem;
      color: #e4e4e7;
      line-height: 1.5;
    }

    .fallback-badge {
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      background: rgba(249, 115, 22, 0.15);
      border: 1px solid rgba(249, 115, 22, 0.3);
      color: var(--orange-highlight);
      font-size: 0.75rem;
      font-weight: 600;
      padding: 0.25rem 0.65rem;
      border-radius: 9999px;
      margin-top: 0.5rem;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(-4px); }
      to { opacity: 1; transform: translateY(0); }
    }

    /* Footer */
    footer {
      border-top: 1px solid var(--border-subtle);
      padding: 2rem;
      text-align: center;
      font-size: 0.82rem;
      color: var(--text-muted);
    }

    footer strong {
      color: var(--text-heading);
    }
  </style>
</head>
<body>

  <header>
    <div class="brand-group">
      <div class="brand-mark">⚡</div>
      <div class="brand-title">Query Fan-Out <span>Engine</span></div>
    </div>
    <div class="header-subtext">Multi-Query Retrieval Decomposition</div>
  </header>

  <main>
    <section class="hero-container">
      <div class="hero-eyebrow">Autonomous Query Expansion</div>
      <h1 class="hero-heading">Decompose broad prompts into <span>focused sub-queries</span>.</h1>
      <p class="hero-description">Break complex requirements into distinct search perspectives, edge cases, and terminology variants to maximize information retrieval accuracy.</p>
    </section>

    <!-- Workspace Input Card -->
    <div class="workspace-card">
      <div class="input-label-row">
        <label for="promptInput" class="field-label">Original Prompt or Question</label>
        <span class="field-hint">Press Ctrl + Enter to run</span>
      </div>

      <textarea id="promptInput" placeholder="e.g. How do I build a production-ready real-time RAG pipeline with high throughput?"></textarea>

      <!-- Presets -->
      <div class="presets-wrapper">
        <div class="presets-title">Sample Prompts</div>
        <div class="presets-list">
          <button type="button" class="preset-button" onclick="setPreset('What are the key trade-offs between PostgreSQL and MongoDB for high write IoT workloads?')">PostgreSQL vs MongoDB for IoT</button>
          <button type="button" class="preset-button" onclick="setPreset('How do I build a production-ready real-time RAG pipeline with high throughput and low latency?')">Real-time RAG Architecture</button>
          <button type="button" class="preset-button" onclick="setPreset('How do I implement secure JWT and session auth in Next.js 14 App Router?')">Next.js 14 Authentication</button>
          <button type="button" class="preset-button" onclick="setPreset('How do I secure an enterprise Kubernetes cluster against supply chain attacks?')">Kubernetes Security</button>
        </div>
      </div>

      <!-- Controls -->
      <div class="controls-grid">
        <div class="control-item">
          <label for="modelSelect" class="field-label">Choose your model</label>
          <select id="modelSelect">
            <option value="openai/gpt-4o-mini" selected>OpenAI: GPT-4o Mini (Ultra Fast & Recommended)</option>
            <option value="deepseek/deepseek-chat">DeepSeek: Chat V3 (High Quality)</option>
            <option value="meta-llama/llama-3.3-70b-instruct">Meta: Llama 3.3 70B Instruct</option>
            <option value="mistralai/mistral-small-24b-instruct-2501">Mistral: Small 24B Instruct</option>
            <option value="anthropic/claude-3-haiku">Anthropic: Claude 3 Haiku</option>
          </select>
        </div>

        <div class="control-item">
          <div class="slider-header">
            <label for="numQueries" class="field-label">Sub-queries</label>
            <span id="numVal" class="slider-value">5</span>
          </div>
          <input type="range" id="numQueries" min="3" max="8" value="5" oninput="document.getElementById('numVal').innerText = this.value">
        </div>

        <button id="btnSubmit" class="btn-submit" onclick="runFanOut()">
          <span>Fan-Out Query</span>
        </button>
      </div>

      <!-- In-Page Error Banner -->
      <div id="errorBanner" class="error-banner">
        <div class="error-banner-header">
          <span>⚠️ Query Fan-Out Notice</span>
        </div>
        <div id="errorMessage" class="error-banner-msg"></div>
        <div style="margin-top: 0.75rem;">
          <button type="button" class="btn-secondary" onclick="retryWithDefaultModel()" style="padding: 0.35rem 0.75rem; font-size: 0.8rem;">
            Retry with Default Model (GPT-4o Mini)
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div id="loaderArea" class="loader-area">
      <div class="loader-wheel"></div>
      <div style="font-weight: 600; color: var(--text-heading); margin-bottom: 0.25rem;">Analyzing prompt dimensions...</div>
      <div style="font-size: 0.85rem; color: var(--text-muted);">Generating multi-angle sub-queries</div>
    </div>

    <!-- Results Presentation -->
    <div id="resultsWrapper" class="results-wrapper">
      <!-- Analysis Summary -->
      <div class="summary-card">
        <div>
          <div class="summary-cell-label">Identified Intent</div>
          <div id="resIntent" class="summary-cell-value">...</div>
          <div id="modelBadge" class="fallback-badge" style="display: none;"></div>
        </div>
        <div>
          <div class="summary-cell-label">Query Complexity</div>
          <div><span id="resComplexity" class="complexity-pill complexity-high">HIGH</span></div>
        </div>
        <div>
          <div class="summary-cell-label">Sub-Queries</div>
          <div id="resCount" class="summary-cell-value">5 Queries</div>
        </div>
      </div>

      <!-- Action Bar -->
      <div class="results-actions-row">
        <h2 class="results-heading">Fanned-Out Sub-Queries</h2>
        <div style="display: flex; gap: 0.5rem;">
          <button class="btn-secondary" onclick="toggleJsonDrawer()">View JSON</button>
          <button class="btn-secondary" onclick="copyAllQueries()">Copy All</button>
        </div>
      </div>

      <!-- JSON Box -->
      <div id="jsonBox" class="json-preview"></div>

      <!-- Query Cards -->
      <div id="cardsGrid" class="cards-grid"></div>
    </div>
  </main>

  <footer>
    <p><strong>Query Fan-Out Engine</strong> • Built for Advanced RAG and Agentic Information Retrieval</p>
  </footer>

  <script>
    let currentPayload = null;

    function setPreset(text) {
      document.getElementById('promptInput').value = text;
      hideError();
    }

    function hideError() {
      const err = document.getElementById('errorBanner');
      if (err) err.style.display = 'none';
    }

    function showError(msg) {
      const err = document.getElementById('errorBanner');
      const msgEl = document.getElementById('errorMessage');
      if (err && msgEl) {
        msgEl.innerText = msg;
        err.style.display = 'block';
        err.scrollIntoView({ behavior: 'smooth' });
      }
    }

    function retryWithDefaultModel() {
      document.getElementById('modelSelect').value = 'openai/gpt-4o-mini';
      hideError();
      runFanOut();
    }

    async function runFanOut() {
      const prompt = document.getElementById('promptInput').value.trim();
      if (!prompt) {
        showError("Please enter a prompt or select a sample question first.");
        return;
      }

      hideError();
      const model = document.getElementById('modelSelect').value;
      const numQueries = parseInt(document.getElementById('numQueries').value, 10);

      const btn = document.getElementById('btnSubmit');
      const loader = document.getElementById('loaderArea');
      const results = document.getElementById('resultsWrapper');

      btn.disabled = true;
      loader.style.display = 'block';
      results.style.display = 'none';

      try {
        const res = await fetch('/api/fanout', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt, model, numQueries })
        });

        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.error || "Failed to process query.");
        }

        const data = await res.json();
        currentPayload = data;
        renderResults(data);
      } catch (err) {
        showError("Error generating sub-queries: " + err.message);
      } finally {
        btn.disabled = false;
        loader.style.display = 'none';
      }
    }

    function renderResults(data) {
      document.getElementById('resIntent').innerText = data.analysis?.intent || "General Inquire";
      
      const compEl = document.getElementById('resComplexity');
      const comp = (data.analysis?.complexity || "medium").toLowerCase();
      compEl.innerText = comp.toUpperCase();
      compEl.className = "complexity-pill complexity-" + comp;

      const queries = data.fanned_queries || [];
      document.getElementById('resCount').innerText = queries.length + " Generated";

      const badgeEl = document.getElementById('modelBadge');
      if (data.analysis?.fallback_triggered) {
        badgeEl.style.display = 'inline-flex';
        badgeEl.innerText = `⚡ Auto-switched to GPT-4o Mini (requested model unavailable)`;
      } else {
        badgeEl.style.display = 'none';
      }

      // JSON Box content
      document.getElementById('jsonBox').innerText = JSON.stringify(data, null, 2);

      // Render Cards
      const grid = document.getElementById('cardsGrid');
      grid.innerHTML = '';

      const categoryMap = {
        decomposition: "Core Sub-Problem",
        perspective: "Alternative Perspective",
        keyword_variant: "Keyword Variant",
        verification: "Prerequisite Check",
        edge_case: "Edge Case & Limits"
      };

      queries.forEach((q) => {
        const card = document.createElement('div');
        card.className = 'query-card';

        const prioText = (q.priority || 'Medium').toUpperCase();
        const prioClass = q.priority === 'high' ? 'prio-high' : '';
        const catName = categoryMap[q.category] || q.category;

        card.innerHTML = `
          <div class="card-header-line">
            <span class="tag-category">${catName}</span>
            <span class="tag-priority ${prioClass}">Priority: ${prioText}</span>
          </div>
          <div>
            <div class="query-statement">"${escapeHtml(q.query)}"</div>
            <div class="target-aspect-text">${escapeHtml(q.targeted_aspect || '')}</div>
          </div>
          <div class="rationale-box">
            <strong>Rationale:</strong> ${escapeHtml(q.rationale || '')}
          </div>
          <div class="card-bottom-bar">
            <span class="search-mode">${q.search_type || 'semantic'} search</span>
            <button type="button" class="btn-card-copy">Copy</button>
          </div>
        `;

        const copyBtn = card.querySelector('.btn-card-copy');
        copyBtn.addEventListener('click', function() {
          navigator.clipboard.writeText(q.query);
          const orig = copyBtn.innerText;
          copyBtn.innerText = "Copied ✓";
          copyBtn.style.backgroundColor = "var(--orange-primary)";
          copyBtn.style.color = "#ffffff";
          setTimeout(() => {
            copyBtn.innerText = orig;
            copyBtn.style.backgroundColor = "";
            copyBtn.style.color = "";
          }, 1500);
        });

        grid.appendChild(card);
      });

      document.getElementById('resultsWrapper').style.display = 'block';
      document.getElementById('resultsWrapper').scrollIntoView({ behavior: 'smooth' });
    }

    function escapeHtml(str) {
      if (!str) return '';
      return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
    }

    function copyAllQueries() {
      if (!currentPayload || !currentPayload.fanned_queries) return;
      const formatted = currentPayload.fanned_queries
        .map((q, i) => `${i + 1}. [${(q.category || '').toUpperCase()}] ${q.query}`)
        .join('\n');
      navigator.clipboard.writeText(formatted);
      alert("All fanned-out queries copied to clipboard!");
    }

    function toggleJsonDrawer() {
      const box = document.getElementById('jsonBox');
      box.style.display = box.style.display === 'block' ? 'none' : 'block';
    }

    // Shortcut: Ctrl/Cmd + Enter
    document.getElementById('promptInput').addEventListener('keydown', function(e) {
      if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
        runFanOut();
      }
    });

    // Default pre-fill
    setPreset("What are the key trade-offs between PostgreSQL and MongoDB for high write IoT workloads?");
  </script>
</body>
</html>
"""


class FanOutRequestHandler(BaseHTTPRequestHandler):
    def _send_response_json(self, status: int, data: dict):
        response_bytes = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(response_bytes)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            response_bytes = HTML_CONTENT.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(response_bytes)))
            self.end_headers()
            self.wfile.write(response_bytes)
        elif self.path == "/health":
            self._send_response_json(200, {"status": "ok", "service": "query-fan-out"})
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        if self.path == "/api/fanout":
            content_length = int(self.headers.get("Content-Length", 0))
            post_body = self.rfile.read(content_length)

            try:
                payload = json.loads(post_body.decode("utf-8"))
                prompt = payload.get("prompt", "").strip()
                model = payload.get("model", DEFAULT_MODEL)
                num_queries = int(payload.get("numQueries", 5))

                if not prompt:
                    self._send_response_json(400, {"error": "Prompt cannot be empty."})
                    return

                engine = QueryFanOut(api_key=DEFAULT_API_KEY, model=model)
                result = engine.generate_fan_out(prompt, num_queries=num_queries)
                self._send_response_json(200, result)

            except Exception as e:
                self._send_response_json(500, {"error": str(e)})
        else:
            self.send_error(404, "Not Found")


def run_server(port: int = PORT):
    server_address = ("", port)
    
    try:
        httpd = ThreadingHTTPServer(server_address, FanOutRequestHandler)
    except OSError:
        # Try alternate port if 5000 is occupied
        port = 5050
        server_address = ("", port)
        httpd = ThreadingHTTPServer(server_address, FanOutRequestHandler)

    url = f"http://localhost:{port}"
    print("\n" + "=" * 70)
    print(" 🚀 QUERY FAN-OUT ENGINE WEB DASHBOARD RUNNING")
    print("=" * 70)
    print(f" 🌐 Localhost URL: {url}")
    print(f" 🎨 Theme: Humanized Editorial (60% Charcoal Black, 30% Crisp White, 10% Studio Orange)")
    print(f" 🤖 Default Model: {DEFAULT_MODEL}")
    print("=" * 70)
    print(" Press Ctrl+C to stop the server.\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.server_close()


if __name__ == "__main__":
    run_server()
