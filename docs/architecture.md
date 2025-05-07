# Architecture Overview

## 1. System Layers

┌────────────────────────┐
│     FastAPI API        │
│  (Routers & Endpoints) │
└────────────────────────┘
            │
            ▼
┌────────────────────────┐
│     Service Layer      │
│ • AgentService         │
│ • ConversationService  │
│ • FileService          │
│ • StorageService       │
└────────────────────────┘
            │
            ▼
┌────────────────────────┐
│     Persistence        │
│ • Elasticsearch (ES)   │
│   – Agents index       │
│   – Conversations idx  │
│   – Messages index     │
│   – Files metadata     │
└────────────────────────┘
            │
            ▼
┌────────────────────────┐
│   Object Storage       │
│   (MinIO / S3-Compat)  │
└────────────────────────┘

┌────────────────────────┐
│      LLM Client        │
│  (OpenAI / HF / etc.)  │
└────────────────────────┘

**Flow at a glance**  
1. HTTP request → FastAPI router  
2. Router → Service Layer  
3. Service:  
   - Reads/writes ES indexes  
   - Calls MinIO for file ops  
   - Calls LLM client for AI replies  
4. Service returns Pydantic model → JSON response  

---

## 2. Key Technology Decisions

- **FastAPI**  
  - Async endpoints, builtin validation, DI  
  - Automatic OpenAPI/Swagger docs  

- **Elasticsearch**  
  - Single source of truth: agents, convs, messages, files metadata  
  - Full-text search, time-based sorting, scalable indexing  
  - Eliminates need for a separate SQL DB  

- **MinIO (S3-compatible)**  
  - On-prem object store, lightweight  
  - Presigned URLs for secure downloads  
  - Keeps binaries out of ES  

- **LLM Client Abstraction**  
  - Unified interface for any provider (OpenAI, HF, Anthropic…)  
  - Central prompt construction, error handling, token tracking  

---

## 3. Context & Token-Usage Management

- **Conversation Context**  
  - On each `send_message`:  
    - Load agent.systemPrompt  
    - Query ES for full history (size≥100 to cover ≥10 turns)  
    - Append user message + attachments  
    - Build flat prompt string  

- **Token Tracking**  
  - After LLM call record:  
    - `prompt_tokens`, `completion_tokens`, `total_tokens`  
  - Store under `token_usage` in message docs  
  - Expose per-message and total usage via `/conversations/{id}/tokens`  

---

## 4. Scaling & Future Extensions

- **Sliding Window**  
  - Replace size=100 with last-N messages window to fit model max tokens  

- **Vector Search / RAG**  
  - Embed messages in vector store, retrieve relevant context on demand  

- **Monitoring & Metrics**  
  - Prometheus for request rate, LLM latency, token consumption  
  - Kibana dashboards for ES performance