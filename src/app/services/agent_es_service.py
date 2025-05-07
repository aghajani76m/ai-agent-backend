import uuid
from datetime import datetime
from typing import List, Optional

from elasticsearch import Elasticsearch, NotFoundError
from app.api.v1.schemas.agents import AgentCreate, AgentInDB, AgentUpdate, AgentOut

INDEX = "agents"

class AgentService:
    def __init__(self, es: Elasticsearch):
        self.es = es

    def create_agent(self, data: AgentCreate) -> AgentInDB:
        agent_id = str(uuid.uuid4())
        now = datetime.utcnow()
        doc = data.dict()
        doc.update({"created_at": now})
        self.es.index(index=INDEX, id=agent_id, document=doc)
        return AgentInDB(id=agent_id, **doc)

    def get_agent(self, agent_id: str) -> AgentOut:
        try:
            res = self.es.get(index=INDEX, id=agent_id)
        except NotFoundError:
            return None
        src = res["_source"]
        return AgentOut(id=res["_id"], **src)

    def list_agents(self, size: int = 10, from_: int = 0) -> List[AgentOut]:
        res = self.es.search(
            index=INDEX,
            body={
                "from": from_,
                "size": size,
                "sort": [{"created_at": {"order": "desc"}}]
            }
        )
        agents = []
        for hit in res["hits"]["hits"]:
            src = hit["_source"]
            agents.append(AgentOut(id=hit["_id"], **src))
        return agents

    def update_agent(self, agent_id: str, data: AgentUpdate) -> Optional[AgentOut]:
        # prepare only provided fields
        body = {"doc": {k: v for k, v in data.dict().items() if v is not None}}
        if not body["doc"]:
            return self.get_agent(agent_id)
        try:
            self.es.update(index=INDEX, id=agent_id, body=body)
        except NotFoundError:
            return None
        return self.get_agent(agent_id)

    def delete_agent(self, agent_id: str) -> bool:
        try:
            self.es.delete(index=INDEX, id=agent_id)
            return True
        except NotFoundError:
            return False