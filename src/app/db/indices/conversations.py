def create_indices(es):
    # Conversations
    es.indices.create(
        index="conversations",
        body={
            "mappings": {
                "properties": {
                    "agent_id": {"type": "keyword"},
                    "created_at": {"type": "date"}
                }
            }
        },
        ignore=400
    )
    # Messages
    es.indices.create(
        index="messages",
        body={
            "mappings": {
                "properties": {
                    "conversation_id": {"type": "keyword"},
                    "role": {"type": "keyword"},
                    "content": {"type": "text"},
                    "token_usage": {
                        "type": "nested",
                        "properties": {
                        "token_input":  { "type": "integer" },
                        "token_output": { "type": "integer" }
                        }
                    },
                    "created_at": {"type": "date"},
                    "attachments": {
                        "type": "nested",
                        "properties": {
                        "id":       { "type": "keyword" },
                        "filename": { "type": "keyword" },
                        "url":      { "type": "keyword" }
                        }
                    }
                }
            }
        },
        ignore=400
    )