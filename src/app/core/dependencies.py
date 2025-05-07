from elasticsearch import Elasticsearch
from app.core.config import settings
from functools import lru_cache
import os
import openai
from app.core.llm_client import llm  

@lru_cache()
def get_es_client() -> Elasticsearch:
    es = Elasticsearch(
        hosts=[{"host": settings.ES_HOST, "port": settings.ES_PORT, "scheme": "http"}],
        http_auth=(settings.ES_USER, settings.ES_PASS) if settings.ES_USER else None,
        verify_certs=False
    )
    return es

def get_llm_client():
    return llm

# src/app/core/dependencies.py
from minio import Minio
from app.core.config import settings

def get_minio_client() -> Minio:
    client = Minio(
        endpoint=settings.MINIO_INTERNAL_ENDPOINT,
        access_key=settings.MINIO_KEY,
        secret_key=settings.MINIO_SECRET,
        secure=settings.MINIO_SECURE,
    )
    # اطمینان از وجود bucket
    if not client.bucket_exists(settings.FILES_BUCKET):
        client.make_bucket(settings.FILES_BUCKET)
    return client

