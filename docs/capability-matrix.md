# Observability Capability Matrix
## Research: What Can We See at Each Level?

This matrix summarizes what each observability approach can capture for AI workloads.
Results validated experimentally using the FLYY.AI demo environment.

---

## Observability Levels

### Level 1 — Zero-Code Instrumentation
Run AI application with `opentelemetry-instrument python app.py`.
No source code modifications.

### Level 2 — Gateway / Reverse Proxy
All AI traffic routed through a monitoring proxy before reaching the LLM API.

### Level 3 — Application Instrumentation
Explicit `tracer.start_as_current_span(...)` calls inside the AI application.

---

## Capability Matrix

| Capability | Zero-Code | Gateway | App Instrumentation |
|---|:---:|:---:|:---:|
| **AI Service Detection** | ⚠️ Partial | ✅ Yes | ✅ Yes |
| **Model Identification** | ⚠️ Partial | ✅ Yes | ✅ Yes |
| **Raw Prompt Capture** | ❌ No | ✅ Yes | ✅ Yes |
| **Sanitized Prompt** | ❌ No | ✅ With PII pipeline | ✅ Yes |
| **Response Content** | ❌ No | ✅ Yes | ✅ Yes |
| **Token Usage** | ⚠️ Partial | ✅ Yes | ✅ Yes |
| **LLM Latency** | ✅ Yes | ✅ Yes | ✅ Yes |
| **HTTP Request/Response** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Tool / Function Calls** | ❌ Limited | ⚠️ Partial | ✅ Yes |
| **Agent Execution Span** | ❌ No | ❌ No | ✅ Yes |
| **Database Access (raw)** | ✅ If DB instrumented | ❌ No | ✅ Yes |
| **DB Access Attribution** | ❌ No (no context) | ❌ No | ✅ With trace context |
| **Declared Data Sources** | ❌ No | ❌ No | ✅ Yes |
| **Actual Data Source Access** | ⚠️ Partial | ❌ No | ✅ Yes |
| **Declared vs Observed Diff** | ❌ No | ❌ No | ✅ Yes |
| **Governance Violations** | ❌ No | ❌ No | ✅ Yes |
| **PII Detection** | ❌ No | ✅ With pipeline | ✅ Yes |
| **Business Intent** | ❌ No | ❌ No | ✅ With explicit spans |
| **User Identity** | ❌ No | ⚠️ If in headers | ✅ Yes |
| **Errors & Failures** | ✅ Yes | ✅ Yes | ✅ Yes |

Legend: ✅ Yes | ⚠️ Partial / Depends | ❌ No

---

## Key Research Findings

### Finding 1: Zero-code has real value but real limits
OpenTelemetry zero-code instrumentation (`opentelemetry-instrument`) automatically captures:
- HTTP request/response lifecycle
- Database connection pool metrics  
- Latency and error rates
- Service dependency graphs

But it **cannot** capture:
- The content of LLM prompts (application-level data, not library metadata)
- Which agent initiated a specific database query (no trace context propagation)
- Whether a tool call was declared vs. undeclared

**Conclusion**: Zero-code is excellent for infrastructure observability, inadequate for AI governance.

### Finding 2: Gateway captures LLM traffic but misses agent internals
A reverse proxy (e.g., LiteLLM, custom nginx + lua) placed between the AI app and OpenAI/Claude API can capture:
- Every prompt and response
- Model name, token counts, provider
- Request timing

But it **cannot** see:
- What database an agent accessed AFTER getting the LLM response
- How the agent decided to use a particular tool
- Whether internal function calls were authorized

**Conclusion**: Gateway is powerful for LLM request visibility but insufficient for agent governance.

### Finding 3: Application instrumentation is required for governance
Only by adding explicit OpenTelemetry spans inside the agent code can we:
- Create an "agent_execution" parent span with declared_sources
- Create child spans for each tool/DB call
- Propagate trace context so DB access is attributed to the correct agent run
- Compare declared vs. observed data sources

This is the approach FLYY.AI uses for agent monitoring.

**Conclusion**: Full AI governance requires application-level instrumentation. 
Zero-code and gateway are complementary but insufficient on their own.

### Finding 4: Trace context propagation is the key to attribution
Without trace context propagation, the OpenTelemetry database instrumentor may record:
```
db.query: SELECT * FROM orders WHERE id = 'ORD-1001'
```
But it cannot automatically attribute this to Agent Run #1042.

With explicit `run_id` passed as a span attribute:
```python
with tracer.start_as_current_span("db.orders.query",
    attributes={"agent.run_id": run_id, "db.name": "ORDERS_DB"}):
    ...
```
The attribution becomes clear, enabling the governance comparison.

---

## Recommendation

For enterprise AI governance, implement **all three levels** as defense-in-depth:

```
Level 1 (Zero-code)    → Infrastructure baseline, free
Level 2 (Gateway)      → LLM prompt audit trail, add per-asset
Level 3 (App Instr.)   → Required for agent governance
```

The FLYY.AI platform uses Level 3 as its primary approach, while documenting 
what Levels 1 and 2 can and cannot provide.
