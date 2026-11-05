# Production Agentic AI: From Zero to Deployment

> **"Most tutorials teach you how to build toy chatbots. This course teaches you how to build autonomous software systems that enterprises can actually trust."**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/badge/managed%20by-uv-blueviolet.svg)](https://github.com/astral-sh/uv)
[![Docker Compose](https://img.shields.io/badge/docker--compose-PostgreSQL%20%7C%20Redis%20%7C%20Phoenix-blue.svg)](docker-compose.yml)
[![Tests](https://img.shields.io/badge/verification%20gate-pytest-brightgreen.svg)](phase-1-foundations/00-environment-and-mocks/tests/)

---

## What Is This Course?

An open-source, hands-on, production-grade masterclass designed for software engineers and AI practitioners building **autonomous agentic systems**.

Instead of 5-line toy demos that hallucinate and crash, you will learn how to design, constrain, test, and deploy mission-critical agents that operate safely in enterprise environments.

Across the course, you will build **Incident Sentinel**: an autonomous AI Site Reliability Engineer that investigates infrastructure alerts, queries database diagnostics via secure MCP tools, consults long-term vector memory, and repairs services under strict human-in-the-loop guardrails.

---

## Curriculum Roadmap

```
Phase 1: Foundations & Deterministic Boundaries
├── 00. Architecture Foundations & Reproducible Environments (Current)
├── 01. Deterministic Control Flow & Core Reasoning Loops
└── 02. Tool Sandboxing, FastMCP, and Schema Governance

Phase 2: Durable State, Graph Orchestration & Human Governance
├── 03. Context Compaction, Short-Term Memory, and Durable State
├── 04. Graph Orchestration, Dynamic Routing, and Multi-Model Fallbacks
└── 05. Enterprise Governance, Guardrails, and Human-in-the-Loop (HITL)

Phase 3: Production Operations & Multi-Tenant Deployment
├── 06. Telemetry, Observability, and Trajectory Evals
├── 07. Asynchronous Execution, Queues, and Fault Tolerance
└── 08. Capstone Enterprise System Deployment
```

---

## Quick Start: Launch Your Environment

### 1. Prerequisites
- **Python 3.12+**
- **[uv](https://github.com/astral-sh/uv)** (Blazing-fast modern Python package manager)
- **Docker Desktop** (For PostgreSQL 16 + pgvector, Redis 7, Arize Phoenix)

### 2. Clone and Setup
```bash
# Clone the repository
git clone https://github.com/your-username/agentic-ai-course.git
cd agentic-ai-course

# Install locked dependencies with uv
uv sync --all-extras

# Configure your environment
cp .env.example .env
# Edit .env and paste your OPENAI_API_KEY
```

### 3. Launch Enterprise Infrastructure Containers
```bash
docker compose up -d
```

### 4. Run the Verification Gate
```bash
# Execute automated test suite for Module 0
uv run pytest phase-1-foundations/00-environment-and-mocks/tests -v
```

### 5. Launch the Interactive Documentation Site
```bash
uv run mkdocs serve
```
Open `http://127.0.0.1:8000` in your browser to read the interactive course chapters with live diagrams.

---

## Repository Structure

```text
agentic-ai-course/
├── docs/                          # Course documentation source (MkDocs Material)
├── docker-compose.yml             # PostgreSQL (pgvector), Redis 7, Arize Phoenix
├── pyproject.toml                 # uv workspace configuration
├── mkdocs.yml                     # Interactive documentation site configuration
├── phase-1-foundations/
│   ├── 00-environment-and-mocks/  # Module 0: Architecture Foundations
│   │   ├── docs/                  # Chapter documentation
│   │   ├── lab/                   # Starter code with typed signatures & # TODO: blocks
│   │   ├── solution/              # Reference production implementation
│   │   └── tests/                 # Automated pytest verification gate
│   ├── 01-deterministic-control-flow/
│   └── 02-mcp-tools-and-sandboxing/
├── phase-2-state-and-orchestration/
│   ├── 03-context-and-durable-state/
│   ├── 04-graph-orchestration-and-routing/
│   └── 05-governance-guardrails-hitl/
└── phase-3-enterprise-operations/
    ├── 06-telemetry-and-trajectory-evals/
    ├── 07-async-queues-and-resilience/
    └── 08-capstone-multitenant-deployment/
```
