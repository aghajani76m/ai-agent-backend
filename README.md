# 🧠 AI Agent Backend Service

This service lets you spin up AI-powered chat agents, manage conversations, upload attachments, and track token usage—all backed by **Elasticsearch** and **MinIO**.

---

## 📚 Documentation

- **API Reference (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)  
- **OpenAPI (ReDoc)**: [http://localhost:8000/redoc](http://localhost:8000/redoc)  
- **Architecture Overview**: [`docs/architecture.md`](docs/architecture.md)

---

## 🚀 Quick Start

### 1. Clone & Configure

```bash
git clone https://github.com/aghajani76m/ai-agent-backend.git
cd ai-agent-backend
```

Open .env and set the following values (like env_example file):

ELASTICSEARCH_URL=http://localhost:9200

MINIO_PUBLIC_ENDPOINT=http://localhost:9000

MINIO_INTERNAL_ENDPOINT=minio:9000

MINIO_KEY=minioadmin

MINIO_SECRET=minioadmin

FILES_BUCKET=attachments

OPENAI_API_KEY=sk-...

### 2. Run with Docker Compose
```bash
docker compose up --build -d
```

This starts:

- Elasticsearch on :9200

- MinIO on :9000 (console on :9001)

- FastAPI app on :8000

### 3. Verify & Initialize
FastAPI’s startup hook will wait for Elasticsearch and then create required indices.

Check the health endpoint:
```bash
curl http://localhost:8000/health
```

You should see:
```bash
{
  "status": "ok",
  "elasticsearch": {
    "cluster_name": "...",
    "version": "8.x.x"
  }
}
```

### 4. Explore API
Open your browser:

- Swagger UI: http://localhost:8000/docs

- ReDoc: http://localhost:8000/redoc

| Path                        | Method | Summary            |
| --------------------------- | ------ | ------------------ |
| `/api/v1/agents`            | GET    | List agents        |
| `/api/v1/agents`            | POST   | Create a new agent |
| `/api/v1/agents/{agent_id}` | GET    | Get agent details  |
| `/api/v1/agents/{agent_id}` | PUT    | Update agent       |
| `/api/v1/agents/{agent_id}` | DELETE | Delete agent       |

### 5. 🧪 Testing
This project includes an end-to-end integration test (tests/test_e2e.py) that spins up real Elasticsearch and MinIO via Testcontainers.

Prerequisites
Docker & Docker Compose

- Python 3.9+

- pip install -r src/app/requirements.txt

### 6. Run tests
```bash
python -m pytest
```

All tests should pass without errors.



