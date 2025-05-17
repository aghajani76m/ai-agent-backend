

agent_index_name = "agents"
def agents_indices_set_mapp(es, number_of_shards=1):
    # Agents
    settings_and_mappings = {
            "mappings": {
                "properties": {
                    "agent_id": {"type": "keyword"},
                    "name": {"type": "keyword"},
                    "description": {"type": "text"},
                    "welcome_message": {"type": "text"},
                    "system_prompt": {"type": "text"},
                    "response_settings": {"type": "object"},
                    "keywords_list": {"type": "keyword"},
                    "llm_model_name": {"type": "keyword"},
                    "release_type": {"type": "keyword"},
                    "role": {"type": "keyword"},
                    "tone": {"type": "keyword"},
                    "creativity": {"type": "keyword"},
                    "response_length": {"type": "keyword"},
                    "language": {"type": "keyword"},
                    "exception_words": {"type": "keyword"},
                    "indices": {"type": "keyword"},
                    "files": {"type": "keyword"},
                    "created_at": {
                        "type": "date",
                        "format": "strict_date_optional_time||EEE MMM dd HH:mm:ss Z yyyy"
                    },
                    "updated_at": {
                        "type": "date",
                        "format": "strict_date_optional_time||EEE MMM dd HH:mm:ss Z yyyy"
                    },
                }
            },
            "settings": {
                "number_of_replicas": 0,
                "number_of_shards": number_of_shards,
            }
    }
    return settings_and_mappings


# es.indices.create(index=agent_index_name, body=agents_indices_set_mapp(1))