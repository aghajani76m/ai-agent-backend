def create_indices(es):
    # Files
    es.indices.create(
        index="files",
        body={
            "mappings": {
                "properties": {
                    "conversation_id": {"type": "keyword"},
                    "filename": {"type": "keyword"},
                    "url": {"type": "keyword"},
                    "content_type": {"type": "keyword"},
                    "size": {"type": "long"},
                    "uploaded_at": {"type": "date"}
                }
            }
        },
        ignore=400
    )