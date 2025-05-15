import uuid
from datetime import datetime
from typing import List, Optional

from elasticsearch import Elasticsearch, NotFoundError
from app.api.v1.schemas.agents import AgentCreate, AgentInDB, AgentUpdate, AgentOut, ResponseSettings
from app.db.indices.agents import agent_index_name
from app.utils.flatten_dict import flatten_dict

INDEX = agent_index_name

class AgentService:
    def __init__(self, es: Elasticsearch):
        self.es = es

    def create_agent(self, data: AgentCreate) -> AgentInDB:
        """
        - Generate a UUID for the new agent  
        - Stamp created_at and updated_at  
        - Serialize the Pydantic model to a flat dict with snake_case keys  
        - Index into Elasticsearch under INDEX  
        """
        agent_id = str(uuid.uuid4())
        now = datetime.utcnow()
        # produce snake_case keys, skip None
        doc = data.dict(by_alias=True, exclude_none=True)
        # set timestamps
        doc["created_at"] = now
        doc["updated_at"] = now

        self.es.index(index=INDEX, id=agent_id, document=doc)
        # return a fully populated Pydantic instance
        return AgentInDB(id=agent_id, **doc)

    def get_agent(self, agent_id: str) -> Optional[AgentOut]:
        """
        - Fetch by ID  
        - Return None if not found  
        - Otherwise wrap _source + _id into AgentOut  
        """
        try:
            res = self.es.get(index=INDEX, id=agent_id)
        except NotFoundError:
            return None

        src = res["_source"]
        return AgentOut(id=res["_id"], **src)

    def list_agents(self, size: int = 10, from_: int = 0) -> List[AgentOut]:
        """
        - Paginated search sorted by created_at descending  
        - Wrap each hit into AgentOut  
        """
        resp = self.es.search(
            index=INDEX,
            body={
                "from": from_,
                "size": size,
                "sort": [{"created_at": {"order": "desc"}}],
            },
        )
        agents: List[AgentOut] = []
        for hit in resp["hits"]["hits"]:
            src = hit["_source"]
            agents.append(AgentOut(id=hit["_id"], **src))
        return agents

    # def update_agent(self, agent_id: str, data: AgentUpdate) -> Optional[AgentOut]:
    #     """
    #     - Build a partial doc from only provided (non-None) fields  
    #     - Always bump updated_at  
    #     - Elasticsearch _update with doc  
    #     - Return None if agent does not exist  
    #     - Otherwise fetch & return the new state  
    #     """
    #     # exclude_unset: فقط فیلدهایی که کاربر صریحاً ارسال کرده بیا
    #     # exclude_none: اگر None بوده حذفش کن
    #     partial = data.dict(
    #         by_alias=True,
    #         exclude_unset=True,
    #         exclude_none=True
    #     )
    #     if not partial:
    #         return self.get_agent(agent_id)

    #     # اگر response_settings ارسال شده، با defaults merge کن
    #     if "response_settings" in partial:
    #         default_rs = ResponseSettings().dict(by_alias=True)
    #         incoming_rs = partial["response_settings"]
    #         partial["response_settings"] = { **default_rs, **incoming_rs }

    #     partial["updated_at"] = datetime.utcnow()

    #     try:
    #         self.es.update(index=INDEX, id=agent_id, body={"doc": partial})
    #     except NotFoundError:
    #         return None

    #     return self.get_agent(agent_id)

    def update_agent(self, agent_id: str, data: AgentUpdate) -> AgentOut:
        """
        - Build a partial doc from only provided (non-None) fields  
        - Always bump updated_at  
        - Elasticsearch _update with doc  
        - Return None if agent does not exist  
        - Otherwise fetch & return the new state  
        """
        partial = data.dict(
            by_alias=True, exclude_unset=True, exclude_none=True
        )
        if not partial:
            return self.get_agent(agent_id)

        # flatten nested payload
        doc = flatten_dict(partial)
        # هم updated_at را ست می‌کنیم
        doc["updated_at"] = datetime.utcnow()

        self.es.update(
            index=INDEX,
            id=agent_id,
            body={"doc": doc}
        )
        return self.get_agent(agent_id)

    def delete_agent(self, agent_id: str) -> bool:
        """
        - Delete document by ID  
        - Return False if not found, True otherwise  
        """
        try:
            self.es.delete(index=INDEX, id=agent_id)
            return True
        except NotFoundError:
            return False