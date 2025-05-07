import os
import time
import json
import urllib
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from testcontainers.elasticsearch import ElasticSearchContainer
from testcontainers.minio import MinioContainer

from app.main import app
from app.core.dependencies import get_es_client, get_minio_client
from app.core.indices import create_indices
from app.core.config import settings

@pytest.fixture(scope="session")
def es_container():
    with ElasticSearchContainer("elasticsearch:8.12.0") as es:
        os.environ["ELASTICSEARCH_URL"] = es.get_url()
        # wait for ES
        time.sleep(60)
        yield es

@pytest.fixture(scope="session")
def minio_container():
    with MinioContainer("minio/minio:RELEASE.2023-01-25T00-19-54Z") as mi:
        host = mi.get_container_host_ip()
        port = mi.get_exposed_port(9000)
        os.environ["MINIO_PUBLIC_ENDPOINT"] = f"http://localhost:{port}"
        os.environ["MINIO_INTERNAL_ENDPOINT"] = f"localhost:{port}"
        os.environ["MINIO_KEY"] = mi.access_key
        os.environ["MINIO_SECRET"] = mi.secret_key
        # os.environ["MINIO_SECURE"] = False
        os.environ["MINIO_BUCKET"] = "files"
        os.environ["FILES_BUCKET"] = "attachments"
        os.environ["MINIO_REGION"] = "us-east-1"
        # give MinIO a moment
        time.sleep(60)
        yield mi

@pytest.fixture(autouse=True)
def init_indices(es_container, minio_container):
    # Create indices and MinIO bucket before app startup
    es = get_es_client()
    create_indices(es)
    # Ensure bucket exists
    minio = get_minio_client()
    if not minio.bucket_exists(settings.FILES_BUCKET):
        minio.make_bucket(settings.FILES_BUCKET)

@pytest.fixture
def client():
    return TestClient(app)

def test_full_flow(client):
    # 1) Create agent
    agent_payload = {
        "name": "TestBot",
        "description": "Integration test bot",
        "welcomeMessage": "Hi!",
        "systemPrompt": "You are a test assistant.",
        "responseSettings": {"tone": "friendly", "verbosity": "short", "creativity": 0.1, "model": "gpt-4o-mini"}
    }
    ag = client.post("/api/v1/agents", json=agent_payload).json()
    assert ag["name"] == "TestBot"
    agent_id = ag["id"]

    # 2) Start conversation
    conv = client.post("/api/v1/conversations", json={"agent_id": agent_id}).json()
    assert conv["agent_id"] == agent_id
    conv_id = conv["id"]

    # 3) Send 10 turns
    for i in range(10):
        resp = client.post(f"/api/v1/conversations/{conv_id}/messages",
                           json={"content": f"Hello {i}", "attachments": []})
        assert resp.status_code == 201
        body = resp.json()
        # Should include at least user+assistant messages
        assert "messages" in body
        assert len(body["messages"]) >= (i + 1) * 2

    # 4) Upload a file
    files = {"upload_file": ("test.txt", b"hello world", "text/plain")}
    f = client.post("/api/v1/files", files=files).json()
    assert f["filename"] == "test.txt"
    file_id = f["id"]

    # 5) List files and get metadata
    lst = client.get("/api/v1/files").json()
    assert any(x["id"] == file_id for x in lst["files"])
    meta = client.get(f"/api/v1/files/{file_id}").json()
    assert meta["url"].startswith("http")

    # 6) Check token usage summary
    toks = client.get(f"/api/v1/conversations/{conv_id}/tokens")
    assert toks.status_code == 200  # بررسی موفق بودن پاسخ
    total_tokens = toks.json()  # چون json() مقدار عددی برمی‌گرداند
    assert isinstance(total_tokens, int)
    assert total_tokens > 0

    # 7) Health endpoint
    health = client.get("/health").json()
    assert health["status"] == "ok"
    assert "elasticsearch" in health