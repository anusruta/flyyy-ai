# FLYYY.AI — AI Governance & Usage Monitor

<div align="center">

**An AI governance and observability platform that safely monitors enterprise AI usage,
redacts PII before persistence, tracks what AI agents actually access,
and compares observed behavior against declared policies.**

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61dafb)](https://react.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791)](https://postgresql.org)
[![OpenTelemetry](https://img.shields.io/badge/OpenTelemetry-SDK-f5a800)](https://opentelemetry.io)

</div>

---

## 1. Problem Statement

A company with 500 employees might use ChatGPT, Claude, internal LLM apps, 
AI coding assistants, RAG systems, and autonomous AI agents. The IT/security 
team knows which AI applications are approved — but **they don't know what's 
actually happening inside those applications**.

### Key questions that currently go unanswered:
- Which AI was used? By whom? When?
- Did a prompt contain PII (name, phone, Aadhaar, PAN)?
- Was this AI being used for its approved purpose?
- Did an AI agent access data sources it wasn't authorized to use?
- Is this AI being used within its declared governance boundary?

FLYYY.AI answers all of these.

---

## 2. Solution

FLYYY.AI is a **three-layer governance platform**:

```
┌─────────────────────────────────────────────────────────────┐
│                     Enterprise AI Apps                       │
│   Customer Support AI  │  HR Assistant  │  Support Agent    │
└──────────────┬──────────────────────────────────────────────┘
               │  SDK instrumentation + API calls
               ▼
┌─────────────────────────────────────────────────────────────┐
│                  Observability Layer                          │
│                                                             │
│  OpenTelemetry Spans:                                       │
│  • agent_execution → declared_sources, run_id               │
│  • llm.completion  → model, tokens, latency                 │
│  • db.query        → source_name, operation, run_id         │
│  • pii.detection   → entities_found                         │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend                            │
│                                                             │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ PII Detect  │  │  Governance  │  │  Retention Job   │  │
│  │ (Presidio   │  │  declared vs │  │  (APScheduler)   │  │
│  │ + Regex)    │  │  observed)   │  │                  │  │
│  └──────┬──────┘  └──────┬───────┘  └──────────────────┘  │
│         │                │                                   │
│         ▼                ▼                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                  PostgreSQL                          │   │
│  │  ai_assets | ai_interactions | agent_runs | policies │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────┬──────────────────────────────────────────────┘
               │  REST API
               ▼
┌─────────────────────────────────────────────────────────────┐
│                  React Dashboard                             │
│  Overview │ AI Assets │ Prompts │ Agent Runs │ Governance   │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Key Features

### 🔐 Privacy-First PII Protection
- Detect PII in prompts **before any database write** (never store raw prompts)
- Detect: NAME, PHONE, EMAIL, PAN, AADHAAR, CREDIT_CARD
- Store sanitized version: `"Call Ramesh at 9876543210"` → `"Call <NAME> at <PHONE>"`
- Store metadata only: `{"NAME": 1, "PHONE": 1}`
- Per-asset configurable prompt monitoring ON/OFF

### 🤖 AI Agent Governance
- Declare which data sources an agent is authorized to use
- Record every actual data source access during execution
- Automatically compute: `unexpected = observed − declared`
- Flag `POLICY_VIOLATION` when unexpected access detected

### 📊 Observability Dashboard
- Real-time overview: assets, interactions, PII incidents, violations
- Per-asset deep-dive: usage, PII breakdown, agent run history
- Prompt monitor: sanitized prompt table with PII badges
- Agent runs: declared vs. observed comparison with violation alerts
- Governance: violation summary, policy management, capability research

### 🔭 OpenTelemetry Integration
- Manual instrumentation with named spans per operation type
- Trace ID propagation: demo app → backend → DB → dashboard
- Research section comparing zero-code vs. gateway vs. app instrumentation

### ⏰ Configurable Retention
- Per-asset retention period (e.g., HR=7 days, Support=30 days)
- Automatic background cleanup via APScheduler

---

## 4. PII Protection Design

### The Core Principle: Sanitize Before Persist

```
❌ WRONG (common mistake):
   Request → PostgreSQL → PII Detection → Redaction
   (raw PII already in DB before redaction runs)

✅ CORRECT (FLYYY.AI approach):
   Request → PII Detection → Redaction → PostgreSQL
   (raw PII never touches the database)
```

### PII Detection Stack

1. **Microsoft Presidio** (primary engine)
   - spaCy NER for PERSON, LOCATION
   - Built-in recognizers for EMAIL_ADDRESS, CREDIT_CARD
   
2. **Custom regex recognizers** (augmenting Presidio)
   - Indian phone numbers: `(?:\+91[\-\s]?)?[6-9]\d{9}\b`
   - PAN cards: `[A-Z]{5}[0-9]{4}[A-Z]{1}`
   - Aadhaar: `\b[2-9]{1}[0-9]{3}\s?[0-9]{4}\s?[0-9]{4}\b`

3. **Tag mapping** to user-friendly labels:
   - `PERSON` → `NAME`
   - `PHONE_NUMBER` → `PHONE`
   - `EMAIL_ADDRESS` → `EMAIL`
   - `IN_PAN` → `PAN`
   - `IN_AADHAAR` → `AADHAAR`

### What Gets Stored

| Field | Stored | Example |
|---|---|---|
| Raw prompt | ❌ Never | `"Call Ramesh at 9876543210"` |
| Sanitized prompt | ✅ Yes | `"Call <NAME> at <PHONE>"` |
| PII type counts | ✅ Yes | `{"NAME": 1, "PHONE": 1}` |
| User identity | ✅ Aliased | `"user_cs_001"` |
| Model / tokens / latency | ✅ Yes | metadata only |

---

## 5. Agent Governance Logic

### Declared vs. Observed

```python
# Policy: what the agent declared it would use
DECLARED_SOURCES = ["FAQ_DB"]

# Runtime: what the agent actually accessed
OBSERVED_SOURCES = ["FAQ_DB", "ORDERS_DB"]  # violation!

# Governance engine:
unexpected = set(observed) - set(declared)
# → {"ORDERS_DB"}

governance_status = "POLICY_VIOLATION" if unexpected else "COMPLIANT"
```

### Example Violation in Dashboard

```
Agent Run #1042
───────────────────────────────────────────

Agent:    Customer Support Agent
Status:   COMPLETED
Started:  2026-08-13 15:30:12 IST

DECLARED SOURCES      OBSERVED SOURCES
─────────────────     ────────────────────
✓ FAQ Database    →   ✓ FAQ Database
                  →   ⚠ Orders Database  ← UNEXPECTED

⚠ POLICY VIOLATION
   Unexpected access to: ORDERS_DB
   This data source was not declared in the agent policy.
```

---

## 6. OpenTelemetry Research

### Three Observability Levels — What Can We Actually See?

We experimentally validated three approaches. See [docs/capability-matrix.md](docs/capability-matrix.md) for the full matrix.

**Level 1 — Zero-Code Instrumentation** (`opentelemetry-instrument python app.py`)
- ✅ Can see: HTTP requests, DB connection pool, latency, errors
- ❌ Cannot see: prompt content, agent tool calls, declared vs. observed sources

**Level 2 — Gateway / Reverse Proxy**
- ✅ Can see: every LLM prompt and response, model, token usage
- ❌ Cannot see: what the agent did after getting the response (DB access, tools)

**Level 3 — Application Instrumentation** (what FLYYY.AI uses)
```python
with tracer.start_as_current_span("agent_execution",
    attributes={"agent.name": "CustomerSupportAgent",
                "agent.run_id": run_id,
                "agent.declared_sources": ["FAQ_DB"]}):
    
    with tracer.start_as_current_span("db.faq.query",
        attributes={"db.name": "FAQ_DB", "db.operation": "SELECT"}):
        result = faq_db.query(topic)

    with tracer.start_as_current_span("db.orders.query",
        attributes={"db.name": "ORDERS_DB", "db.operation": "SELECT"}):
        result = orders_db.get_order(order_id)  # ← flagged as violation
```
- ✅ Can see: everything — agent identity, tools, DB access, declared vs. observed

### Key Limitation (Honestly Documented)

> **Database instrumentation without trace context propagation cannot attribute a DB access to a specific agent run.**
>
> Zero-code SQLAlchemy instrumentation records that `ORDERS_DB was queried` but doesn't know it was initiated by agent run #1042. This attribution requires either (a) explicit `run_id` span attributes, or (b) trace context propagation from the agent span to the DB call.
>
> FLYYY.AI solves this with explicit `run_id` propagation in application instrumentation.

---

## 7. Database Schema

### `ai_assets`
```sql
CREATE TABLE ai_assets (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,        -- 'llm' | 'agent'
    provider VARCHAR(100),
    model VARCHAR(100),
    declared_purpose TEXT,
    prompt_monitoring BOOLEAN DEFAULT TRUE,
    retention_days INTEGER DEFAULT 30,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### `ai_interactions`
```sql
CREATE TABLE ai_interactions (
    id UUID PRIMARY KEY,
    asset_id UUID REFERENCES ai_assets(id),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    user_id VARCHAR(255),            -- aliased, never raw identity
    sanitized_prompt TEXT,           -- NULL when monitoring OFF
    pii_detected JSONB DEFAULT '{}', -- {"NAME": 1, "PHONE": 1}
    model VARCHAR(100),
    input_tokens INTEGER,
    output_tokens INTEGER,
    latency_ms INTEGER,
    status VARCHAR(50) DEFAULT 'success',
    trace_id VARCHAR(255)
    -- NOTE: No raw_prompt column. It never exists.
);
```

### `agent_runs` + `access_events`
```sql
CREATE TABLE agent_runs (
    id UUID PRIMARY KEY,
    asset_id UUID REFERENCES ai_assets(id),
    started_at TIMESTAMPTZ DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    status VARCHAR(50),
    declared_sources JSONB DEFAULT '[]',
    observed_sources JSONB DEFAULT '[]',
    violation BOOLEAN DEFAULT FALSE,
    trace_id VARCHAR(255)
);

CREATE TABLE access_events (
    id UUID PRIMARY KEY,
    run_id UUID REFERENCES agent_runs(id),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    source_name VARCHAR(255),   -- "FAQ_DB", "ORDERS_DB"
    operation VARCHAR(50),       -- "SELECT", "INSERT"
    status VARCHAR(50)
);
```

---

## 8. Security & Privacy Considerations

### Data Minimization
- Raw prompts: **never persisted** anywhere in the system
- User IDs: stored as aliases (`user_cs_001`), not real names
- PII metadata: counts only, not the actual PII values
- Prompt content: only stored when `prompt_monitoring = true`

### Access Control (Production Extension)
- In production: restrict governance dashboard to security/IT admins
- API endpoints should require JWT authentication
- DB credentials via secrets manager (not env variables)

### Prompt Injection Awareness
- The PII detection layer sanitizes prompts regardless of content
- Even if a prompt says "ignore monitoring and reveal..." — it still gets sanitized before storage
- The monitoring system operates independently of the AI's output

### Retention Design
- Per-asset configurable retention (e.g., HR=7 days, Support=30 days)
- Automatic background deletion — data doesn't accumulate indefinitely
- On deletion: interaction record removed, PII metadata removed

---

## 9. Known Limitations

### What We Cannot Observe Without Code Changes

1. **Closed-box LLM APIs**: If an AI application uses OpenAI via a third-party wrapper that doesn't propagate trace context, we cannot automatically attribute calls to a specific agent run.

2. **Encrypted traffic at the network layer**: Zero-code network monitoring cannot inspect HTTPS body content without TLS termination.

3. **Multi-turn conversation context**: We capture per-request prompts but not the full multi-turn conversation memory if the AI app manages this internally.

4. **System prompt content**: If an AI application sets a system prompt internally without passing it through our monitoring API, we don't capture it.

5. **AI model internal reasoning**: Chain-of-thought reasoning that happens inside the model (e.g., GPT-4o thinking) is not observable from the outside.

6. **Semantic intent**: We know a DB was accessed but not necessarily *why* the agent chose to access it. Business intent requires explicit application-level annotation.

### PII Detection Limitations

- **False positives**: Long numeric order IDs (e.g., `9876543210`) may be detected as Indian phone numbers. Mitigated by context scoring.
- **False negatives**: Heavily formatted or obfuscated PII (e.g., `r.a.m.e.s.h@co.`) may evade regex-based detection.
- **Name ambiguity**: "Apple" could be a company or a person's name — spaCy NER may misclassify.
- **Non-English content**: PII in Indian regional languages is not detected by the English spaCy model.

---

## 10. What This System Cannot Do (Honest Assessment)

We explicitly chose not to claim observability we don't have:

| Claim | Reality |
|---|---|
| "We monitor everything" | ❌ We monitor what we can instrument |
| "Zero-code sees all agent actions" | ❌ Zero-code misses agent-level semantics |
| "All PII is always detected" | ❌ NER has false negatives, especially for unusual names |
| "This works without code changes" | ⚠️ Basic telemetry yes, governance no |

The honest answer: **full AI governance requires application-level instrumentation**.

---

## 11. Quick Start

### Prerequisites
- Docker + Docker Compose
- Python 3.11+ (for running demo apps locally)

### 1. Clone and configure
```bash
git clone https://github.com/your-username/flyy-ai-governance
cd flyy-ai-governance
cp .env.example .env
```

### 2. Start all services
```bash
docker-compose up --build
```

This starts:
- PostgreSQL at `localhost:5432`
- FastAPI backend at `http://localhost:8000`
- React frontend at `http://localhost:3000`

### 3. Install demo dependencies
```bash
cd demo
pip install httpx
```

### 4. Run the full demo
```bash
python run_demo.py
```

This populates the dashboard with:
- 27 AI interactions across 2 LLM apps
- 5 agent runs (3 compliant, 2 violations)
- PII detections across 6 types

### 5. View the dashboard
Open: **http://localhost:3000**

### 6. Run tests
```bash
cd backend
pip install -r requirements.txt
python -m spacy download en_core_web_lg
pytest tests/ -v
```

---

## 12. API Reference

Base URL: `http://localhost:8000`

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/api/assets` | List all AI assets |
| POST | `/api/assets` | Create AI asset |
| GET | `/api/assets/{id}` | Asset detail with stats |
| PATCH | `/api/assets/{id}` | Update asset (toggle monitoring, etc.) |
| GET | `/api/assets/{id}/policy` | Get asset policy |
| PUT | `/api/assets/{id}/policy` | Update asset policy |
| POST | `/api/interactions` | Record interaction (PII pipeline runs) |
| GET | `/api/interactions` | List interactions |
| GET | `/api/interactions/pii-summary` | PII type breakdown |
| POST | `/api/agent-runs` | Start agent run |
| POST | `/api/agent-runs/{id}/access-events` | Record access event |
| POST | `/api/agent-runs/{id}/complete` | Complete run + governance eval |
| GET | `/api/agent-runs` | List agent runs |
| GET | `/api/agent-runs/{id}` | Run detail with access events |
| GET | `/api/analytics/overview` | Summary stats |
| GET | `/api/analytics/usage-over-time` | Last 7 days by day |
| GET | `/api/analytics/pii-by-asset` | PII breakdown per asset |
| GET | `/api/analytics/pii-types` | PII type aggregates |
| GET | `/api/analytics/agent-stats` | Agent run stats |
| GET | `/api/governance/violations` | List violations |
| GET | `/api/governance/policies` | List policies |
| GET | `/api/governance/summary` | Governance summary |

Interactive docs: **http://localhost:8000/docs**

---

## 13. Project Structure

```
flyy-ai-governance/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app entry point
│   │   ├── config.py                # Pydantic settings
│   │   ├── database.py              # Async SQLAlchemy
│   │   ├── models/models.py         # ORM models
│   │   ├── schemas/schemas.py       # Request/response schemas
│   │   ├── api/
│   │   │   ├── assets.py            # AI asset CRUD
│   │   │   ├── interactions.py      # Interaction + PII pipeline
│   │   │   ├── agent_runs.py        # Agent run tracking
│   │   │   ├── analytics.py         # Analytics aggregations
│   │   │   └── governance.py        # Governance/violations
│   │   ├── services/
│   │   │   ├── pii_detector.py      # Presidio + regex PII
│   │   │   ├── governance.py        # Declared vs observed
│   │   │   └── retention.py         # APScheduler cleanup
│   │   └── observability/
│   │       └── telemetry.py         # OpenTelemetry setup
│   ├── seed_data.py                 # Sample data seeder
│   ├── tests/                       # pytest test suite
│   └── Dockerfile
│
├── demo/
│   ├── mock_llm.py                  # Mock LLM (no API key needed)
│   ├── customer_support.py          # Demo app 1: LLM with PII
│   ├── hr_assistant.py              # Demo app 2: LLM without PII
│   ├── support_agent.py             # Demo app 3: Agent with violations
│   ├── run_demo.py                  # Master demo runner
│   └── tools/
│       ├── faq_db.py                # Declared: FAQ tool
│       └── orders_db.py             # Undeclared: Orders tool (violation)
│
├── frontend/
│   ├── src/
│   │   ├── pages/                   # 6 dashboard pages
│   │   ├── components/              # Reusable components
│   │   ├── services/api.js          # Axios API client
│   │   └── App.jsx                  # Router + layout
│   ├── Dockerfile
│   └── nginx.conf
│
├── docs/
│   ├── capability-matrix.md         # Observability research matrix
│   └── research.md                  # Extended research notes
│
├── docker-compose.yml
├── .env.example
└── README.md                        # This file
```

---

## 14. Future Improvements

- **Real LLM integration**: Switch mock LLM to OpenAI/Claude/Gemini with API key
- **OpenLLMetry**: Integrate Traceloop's OpenLLMetry for standardized LLM spans
- **RBAC**: Role-based access control (admin, security analyst, read-only)
- **Alerting**: Email/Slack notifications on governance violations
- **Multi-tenant**: Separate namespacing per department
- **Streaming PII**: Real-time PII detection on streaming LLM responses
- **LLM gateway**: Deploy nginx + lua proxy as Level 2 observability layer
- **Export**: PDF governance reports, CSV exports
- **Audit log**: Immutable audit trail for compliance

---

## 15. What FLYYY.AI Is Building (In One Sentence)

> An enterprise AI governance platform that answers: **who used which AI, for what purpose, with what data, and did it violate policy** — while ensuring sensitive information is never stored in plaintext.

---

*Built as part of the FLYYY.AI Technical Assessment — demonstrating AI observability, PII-safe monitoring, and governance-first design.*
