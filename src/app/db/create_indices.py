from app.db.indices.agents import agent_index_name, agents_indices_set_mapp

def create_indices(es):
    # # Agents
    # es.indices.create(
    #     index="agents",
    #     body={
    #         "mappings": {
    #             "properties": {
    #                 "name": {"type": "keyword"},
    #                 "description": {"type": "text"},
    #                 "welcome_message": {"type": "text"},
    #                 "system_prompt": {"type": "text"},
    #                 "response_settings": {"type": "object"},
    #                 "created_at": {"type": "date"},
    #                 "updated_at": {"type": "date"},
    #                 "keywords_list": {"type": "keyword"},
    #                 "llm_model_name": {"type": "keyword"},
    #                 "release_type": {"type": "keyword"},
    #                 "tone": {"type": "keyword"},
    #                 "creativity": {"type": "keyword"},
    #                 "response_length": {"type": "keyword"},
    #                 "language": {"type": "keyword"},
    #                 "exception_words": {"type": "keyword"},
    #                 "indices": {"type": "keyword"}
    #             }
    #         }
    #     },
    #     ignore=400
    # )
    # # Conversations
    # es.indices.create(
    #     index="conversations",
    #     body={
    #         "mappings": {
    #             "properties": {
    #                 "agent_id": {"type": "keyword"},
    #                 "created_at": {"type": "date"}
    #             }
    #         }
    #     },
    #     ignore=400
    # )
    # # Messages
    # es.indices.create(
    #     index="messages",
    #     body={
    #         "mappings": {
    #             "properties": {
    #                 "conversation_id": {"type": "keyword"},
    #                 "role": {"type": "keyword"},
    #                 "content": {"type": "text"},
    #                 "token_usage": {
    #                     "type": "nested",
    #                     "properties": {
    #                     "token_input":  { "type": "integer" },
    #                     "token_output": { "type": "integer" }
    #                     }
    #                 },
    #                 "created_at": {"type": "date"},
    #                 "attachments": {
    #                     "type": "nested",
    #                     "properties": {
    #                     "id":       { "type": "keyword" },
    #                     "filename": { "type": "keyword" },
    #                     "url":      { "type": "keyword" }
    #                     }
    #                 }
    #             }
    #         }
    #     },
    #     ignore=400
    # )
    # # Files
    # es.indices.create(
    #     index="files",
    #     body={
    #         "mappings": {
    #             "properties": {
    #                 "conversation_id": {"type": "keyword"},
    #                 "filename": {"type": "keyword"},
    #                 "url": {"type": "keyword"},
    #                 "content_type": {"type": "keyword"},
    #                 "size": {"type": "long"},
    #                 "uploaded_at": {"type": "date"}
    #             }
    #         }
    #     },
    #     ignore=400
    # )
    es.indices.create(index=agent_index_name, body=agents_indices_set_mapp(1), ignore=400)