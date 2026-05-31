# agentmemory vs. Graphiti — Agent Memory for a Local Claude Code Project

**Research date:** 2026-05-31
**Question:** Which agent-memory project is the better fit for a *local* (self-hosted / offline-capable) Claude Code setup — [`rohitg00/agentmemory`](https://github.com/rohitg00/agentmemory) or [`getzep/graphiti`](https://github.com/getzep/graphiti)?
**Method:** Fan-out web search → primary-source fetch (both repos, the Zep arXiv paper, FalkorDB/Neo4j docs, independent benchmarks) → adversarial cross-check of claims → synthesis.

---

## TL;DR Recommendation

> **For a local Claude Code project, start with `agentmemory`.** It is purpose-built for coding agents, installs as a native Claude Code plugin (12 lifecycle hooks + MCP), runs fully offline on SQLite + local embeddings with **zero external databases**, and incurs ~$0 cost in local mode. It captures memory automatically with no manual API calls.
>
> **Choose `Graphiti` instead if** your real need is a *general-purpose, temporally-aware knowledge graph* — relationship/fact reasoning that changes over time, audited fact validity windows, multi-app shared memory — and you are willing to run a graph database (FalkorDB/Neo4j/Kuzu) and pay per-episode LLM extraction cost. Graphiti is far more mature (26.8k★ vs. a brand-new project) and battle-tested, but it is heavier and not coding-agent-specific.
>
> **Hybrid option:** They are not mutually exclusive. You can run agentmemory as the day-to-day coding-session memory and add Graphiti's MCP server when you specifically want a queryable temporal knowledge graph. Both are Apache-2.0 and both ship MCP servers.

Confidence: **High** on the factual comparison below; **Medium** on agentmemory's production durability (project is very new and depends on a less-common runtime — see Risks).

---

## Side-by-Side Comparison

| Dimension | **agentmemory** (rohitg00) | **Graphiti** (getzep) |
|---|---|---|
| **Primary purpose** | Persistent memory for **AI coding agents** (Claude Code, Cursor, etc.) | General **temporal knowledge-graph** memory layer for any AI agent |
| **Memory model** | Triple-stream: **BM25 + vector + knowledge-graph**, fused with Reciprocal Rank Fusion (RRF, k=60); 4-tier consolidation (Working→Episodic→Semantic→Procedural) with Ebbinghaus-curve decay | **Bi-temporal knowledge graph** — entities, fact/edge triplets with validity windows, episodes as provenance; non-lossy incremental updates |
| **Retrieval** | Hybrid BM25 + vector cosine + graph traversal; session-diversified output | Hybrid semantic + BM25 + graph traversal + **cross-encoder reranking** |
| **Default storage** | **SQLite** + in-memory vector index — **no external DB** | Requires a graph DB: **FalkorDB** (default), Neo4j 5.26+, Kuzu, or Amazon Neptune |
| **Language / runtime** | TypeScript (Node.js ≥ 20), on the **iii-engine** runtime (worker/function/trigger) | **Python 3.10+**, `pip install graphiti-core` |
| **Embeddings** | **Local `all-MiniLM-L6-v2` by default (free, offline)**; also OpenAI, Gemini, Voyage, Cohere, OpenRouter | OpenAI default; Gemini, Voyage, **Ollama (local via OpenAI-compatible endpoint)**, sentence-transformers |
| **LLM usage** | **Optional** — "no-op" is the factory default; compression only if configured (Anthropic/OpenAI/Gemini/Ollama/LM Studio/vLLM) | **Required & per-episode** — every ingestion calls an LLM for entity/edge extraction; models must support Structured Output |
| **Cost (typical)** | **$0 fully local**; ~$10/yr (~170K tokens) with an API provider | LLM extraction cost on **every** episode; can be significant at scale |
| **Claude Code integration** | **Native plugin**: `/plugin install agentmemory` → 12 hooks, 8 skills, 53 MCP tools; auto-capture, zero manual calls | **MCP server** (`mcp_server/`) for Claude/Cursor; manual config; no coding-agent lifecycle hooks |
| **Local / offline** | **Fully self-hosted, zero external calls** (SQLite + local embed + optional local LLM); BM25 works offline even without embeddings | Local-capable (FalkorDB/Kuzu + Ollama), but still needs a running graph DB and LLM endpoint |
| **Benchmarks** | LongMemEval-S: **95.2% R@5, 88.2% MRR**; proprietary coding bench: 0.967 R@5, ~14ms latency | Sub-second retrieval (~300ms P95); outperforms MemGPT on DMR (per Zep paper); higher token/memory footprint than vector-only |
| **License** | Apache-2.0 | Apache-2.0 |
| **Maturity / community** | **Very new** (≈ May 2026); ~21.8K LOC, 950+ tests; small/single-author project | **Mature**: ~26.8k★, 2.7k forks, 195+ releases (v0.29.1), active Discord; backed by Zep + arXiv paper (2501.13956) |
| **Scalability path** | Swap in `iii-database`/`iii-pubsub`/`iii-queue` workers for multi-instance scale | Graph DB scales to large graphs; concurrency via `SEMAPHORE_LIMIT`; Zep cloud reports sub-200ms at scale |

---

## Detailed Findings

### Architecture & memory model
- **agentmemory** runs as a persistent local service (ports 3111 REST / 3112 streams / 3113 viewer / 49134 WS) on the iii-engine. Its capture pipeline is coding-agent-aware: `PostToolUse` hook → SHA-256 dedup (5-min window) → privacy filter (strips secrets/API keys) → raw store → optional LLM compression → embed → index in BM25 + vector → optional KG extraction. `SessionStart` injects a token-budgeted (default 2000 tokens) hybrid-search context back into the conversation. ([repo](https://github.com/rohitg00/agentmemory), [alphasignal](https://alphasignalai.substack.com/p/how-agentmemory-works-and-how-to))
- **Graphiti** models memory as a living temporal graph. Edges carry validity intervals (when a fact became true / was superseded), so historical state is preserved non-lossily and queries can be time-scoped. This is its core differentiator vs. flat vector stores and vs. batch GraphRAG. ([Neo4j blog](https://neo4j.com/blog/developer/graphiti-knowledge-graph-memory/), [arXiv 2501.13956](https://arxiv.org/abs/2501.13956))

### Local / offline suitability (the deciding axis for this project)
- **agentmemory** is the stronger "local-first" story: default SQLite + `all-MiniLM-L6-v2` embeddings + optional local LLM = **no external services, no API keys, no cloud**. BM25 still works even if embeddings are disabled. ([repo](https://github.com/rohitg00/agentmemory))
- **Graphiti** *can* run locally (FalkorDB or Kuzu + Ollama), but you must operate a graph database and an LLM endpoint, and every ingested episode triggers LLM entity-extraction — heavier to run offline and not free even locally (compute/latency). ([FalkorDB docs](https://docs.falkordb.com/agentic-memory/graphiti-mcp-server.html), [mcp_server README](https://github.com/getzep/graphiti/blob/main/mcp_server/README.md))

### Integration effort with Claude Code
- **agentmemory**: lowest friction. `/plugin marketplace add rohitg00/agentmemory` → `/plugin install agentmemory`. Hooks auto-capture every tool use; no `memory.add()` calls. Falls back to a 7-tool core MCP server when the backend is offline. ([README](https://github.com/rohitg00/agentmemory/blob/main/README.md))
- **Graphiti**: register its MCP server in the client config (Docker-Compose with FalkorDB/Neo4j). Works with Claude Desktop/Code as an MCP client but has **no coding-session lifecycle hooks** — capture is more manual/tool-driven. ([Zep MCP docs](https://help.getzep.com/graphiti/getting-started/mcp-server))

### Performance
- **agentmemory** reports very low local retrieval latency (~14ms on its proprietary coding bench) and 95.2% R@5 on LongMemEval-S. Note the proprietary coding benchmark is self-reported and not independently reproduced. ([LONGMEMEVAL.md](https://github.com/rohitg00/agentmemory/blob/main/benchmark/LONGMEMEVAL.md))
- **Graphiti** delivers sub-second / ~300ms P95 retrieval without LLM-in-the-loop summarization, but independent comparisons flag a **large memory/token footprint** (Mem0 paper cites 600K+ tokens/conversation for graph memory) and per-episode LLM extraction cost. ([Codex blog](https://codex.danielvaughan.com/2026/03/30/graphiti-agent-memory-store/), [dev.to benchmark](https://dev.to/juandastic/i-benchmarked-graphiti-vs-mem0-the-hidden-cost-of-context-blindness-in-ai-memory-4le3))

---

## Risks & Caveats

**agentmemory**
- **Immaturity:** brand-new (≈May 2026), effectively single-maintainer, small ecosystem. API/stability churn is likely.
- **Unusual runtime dependency:** requires the **iii-engine** (prebuilt binary or Docker) — a less-common runtime that adds an install/ops dependency and a degree of lock-in.
- **Self-reported benchmarks:** the headline coding-agent numbers come from the project's own harness; treat as indicative, not independently validated.

**Graphiti**
- **Operational weight:** needs a graph DB service + an LLM endpoint; heavier to stand up and keep running locally.
- **Per-episode LLM cost/latency:** entity/edge extraction on every write; can be expensive/slow at high write volume.
- **Entity resolution noise:** LLM extraction + entity merging is an unsolved hard problem; graph quality degrades without pruning strategy.
- **Not coding-agent specialized:** no native Claude Code hooks; you build the capture flow yourself.

---

## Decision Guide

- **"I want drop-in memory for my local Claude Code, offline, free, minimal ops."** → **agentmemory.**
- **"I need durable, audited, time-aware *relationship* memory shared across many apps and I can run a graph DB."** → **Graphiti.**
- **"I want the best of both."** → agentmemory for coding-session capture/recall + Graphiti MCP for an explicit temporal knowledge graph.
- **"Stability/track record matters most right now."** → Graphiti (26.8k★, 195+ releases, enterprise backing) is the lower-risk, more proven choice; revisit agentmemory as it matures.

---

## Sources

- [rohitg00/agentmemory (repo + README + benchmarks)](https://github.com/rohitg00/agentmemory)
- [agentmemory LongMemEval results](https://github.com/rohitg00/agentmemory/blob/main/benchmark/LONGMEMEVAL.md)
- [How agentmemory works (AlphaSignal)](https://alphasignalai.substack.com/p/how-agentmemory-works-and-how-to)
- [getzep/graphiti (repo)](https://github.com/getzep/graphiti)
- [Graphiti MCP server README](https://github.com/getzep/graphiti/blob/main/mcp_server/README.md)
- [Zep / Graphiti MCP server docs](https://help.getzep.com/graphiti/getting-started/mcp-server)
- [Graphiti MCP + FalkorDB docs](https://docs.falkordb.com/agentic-memory/graphiti-mcp-server.html)
- [Graphiti: Knowledge Graph Memory (Neo4j blog)](https://neo4j.com/blog/developer/graphiti-knowledge-graph-memory/)
- [Zep: A Temporal Knowledge Graph Architecture for Agent Memory (arXiv 2501.13956)](https://arxiv.org/abs/2501.13956)
- [Graphiti as agent memory store — analysis (Codex blog)](https://codex.danielvaughan.com/2026/03/30/graphiti-agent-memory-store/)
- [Graphiti vs Mem0 benchmark (dev.to)](https://dev.to/juandastic/i-benchmarked-graphiti-vs-mem0-the-hidden-cost-of-context-blindness-in-ai-memory-4le3)
