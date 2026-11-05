---
name: course-authoring
description: Master guide and quality protocol for authoring the "Production Agentic AI: From Zero to Deployment" course. Enforces engaging, Karpathy/Stripe-style conversational tone, learner-first pedagogy, real infrastructure (no toy mocks), and mandatory subagent review by a beginner/intermediate reader persona.
---

# Production Agentic AI Course Authoring Guide & Reader Protocol

This skill governs the authoring, tone, architecture, and review process for the course:
**"Production Agentic AI: From Zero to Deployment"**.

---

## 1. Core Vision & The Continuous Domain

* **Course Title:** Production Agentic AI: From Zero to Deployment
* **Continuous Domain:** **Incident Sentinel** — An autonomous AI Site Reliability Engineer (SRE).
* **Guiding Philosophy:**
  1. **First Principles First:** Build core loops in standard Python before adopting orchestration frameworks.
  2. **Deterministic Boundaries:** Constrain stochastic models with strict Pydantic schemas, finite state machines, step ceilings, and cost budgets.
  3. **Real Infrastructure (Zero Toy Mocks):** Always connect to real tools (PostgreSQL with `pgvector`, Redis 7, Arize Phoenix, real model APIs or Ollama/vLLM). Never build toy mock servers or canned if-statement simulators.
  4. **Continuous Automated Verification:** Every module includes real, runnable `pytest` test suites verifying the code.

---

## 2. Pedagogical Style: The Karpathy / Stripe Standard

Every chapter must read like a world-class, engaging masterclass—never a dry military compliance manual.

### Writing Rules:
1. **Engaging, Conversational Voice:** Write like an experienced, empathetic mentor. Use active voice, natural enthusiasm, and relatable analogies (e.g., the dreaded 3:00 AM database outage).
2. **The "Why" Before the "What":** Never show code without first explaining what problem it solves and why naive solutions fail.
3. **No Unexplained Jargon:** When introducing a technical concept (e.g., "ReAct loop", "idempotency key", "context window compaction"), define it in plain English with an intuitive analogy first.
4. **Digestible & Not Overwhelming:**
   - Keep paragraphs focused (3 to 5 sentences).
   - Use bold highlights, summary tables, and clear callouts.
   - Keep chapters between 1,000 and 1,800 words (8 to 12 minutes reading time).
   - Keep code blocks in documentation under 25 lines (displaying core logic; point to `lab/` for full scripts).

---

## 3. Standard Chapter Blueprint

Every module documentation chapter (`docs/index.md`) must follow this structure:

1. 🌟 **Chapter Overview & What You Will Build**
   - High-energy opening hook.
   - Bulleted list of the exact practical skills and code the reader will build.
2. 💡 **The Real-World Scenario (The Problem in Plain English)**
   - Relatable production outage or engineering challenge.
   - "Toy Prototype vs. Production Reality" comparison table.
3. 🧠 **Mental Model & Architecture Diagram**
   - Clean Mermaid diagram (7 to 9 nodes) with standard shapes:
     - Rectangles `[Text]` for deterministic code/functions.
     - Hexagons `{{Text}}` for stochastic model calls.
     - Cylinders `[(Text)]` for databases, vector tables, and caches.
     - Subgraphs `subgraph Name` for Docker/MCP boundaries.
   - Plain-English walkthrough explaining how the pieces talk to each other.
4. 🛠️ **Engineering Deep Dive**
   - The core mechanics explained with intuitive mental models and code snippets.
5. 🧪 **Hands-on Lab Protocol**
   - Clear, step-by-step instructions on exploring `lab/`, resolving `# TODO:` blocks, and using infrastructure containers.
6. 🚀 **Verification Gate**
   - The exact `pytest` command that proves production readiness.
   - Explanation of what each test verifies and what green tests mean.
7. ⏭️ **What's Next**
   - A motivating victory lap and teaser connecting to the next chapter.

---

## 4. Mandatory Reader Persona Subagent Protocol

Whenever a new module or chapter is drafted or modified, you **MUST** spin up a subagent to evaluate the text from the perspective of a reader.

### The Subagent Role: "Course Reader & Learning Critic"
* **Persona:** A software engineer who is proficient in Python but brand new to Agentic AI.
* **Review Checklist:**
  1. **Comprehension:** Can a newcomer understand the concepts without re-reading sentences? Are there unexplained acronyms or hidden assumptions?
  2. **Cognitive Load & Length:** Is the chapter overwhelming, dense, or exhausting? Where does the reader's attention drift?
  3. **Tone & Motivation:** Does the chapter create genuine excitement to build? Does it feel like a helpful mentor or a dry textbook?
  4. **Actionability:** Are the hands-on lab instructions crystal clear? Would a reader know exactly what to do next?
* **Action:** Incorporate the reader subagent's feedback into the draft before presenting the module to the user.
