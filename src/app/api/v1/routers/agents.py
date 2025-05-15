from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from elasticsearch import Elasticsearch

from app.api.v1.schemas.agents import AgentCreate, AgentOut, AgentUpdate
from app.services.agent_es_service import AgentService
from app.core.dependencies import get_es_client

router = APIRouter(prefix="/agents", tags=["agents"])


def get_agent_service(es: Elasticsearch = Depends(get_es_client)):
    return AgentService(es)


@router.post(
    "",
    response_model=AgentOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new AI Agent",
    description="""
    Create an agent with the following properties:
    - **name**: unique identifier for the agent  
    - **description**: optional detailed description  
    - **welcomeMessage**: text sent when a conversation starts  
    - **systemPrompt**: global instructions for the LLM  
    - **responseSettings**: selection of tone, verbosity, creativity, model, release_type, response_length, language  
    - **role**: choose a role for LLM
    - **keywords_list**: list of keywords the agent should recognize  
    - **exception_words**: words to be filtered or excluded  
    - **indices**: names of search indices to use in RAG  
    - **files**: related file paths (scripts, notebooks, etc.)
    """,
    responses={
        201: {
            "description": "Agent successfully created",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "name": "Support Bot",
                        "description": "Helps with software issues",
                        "welcomeMessage": "Hello!",
                        "systemPrompt": "You are a helpful assistant.",
                        "responseSettings": {
                            "tone": "professional",
                            "verbosity": "detailed",
                            "creativity": 0.7,
                            "model": "gpt-4o",
                            "release_type": "stable",
                            "response_length": "medium",
                            "language": "en"
                        },
                        "role": "دستیار هوشمند",
                        "keywords_list": ["support", "troubleshoot"],
                        "exception_words": ["error", "fail"],
                        "indices": ["index1", "index2"],
                        "files": ["script.py", "notebook.ipynb"],
                        "created_at": "2025-05-07T12:00:00Z",
                        "updated_at": "2025-05-07T12:00:00Z"
                    }
                }
            }
        }
    }
)
def create_agent(
    payload: AgentCreate,
    service: AgentService = Depends(get_agent_service)
):
    """
    Create a new AI Agent instance.
    ---
    Fields:
    - name (str): Unique name of the agent.
    - description (str, optional): Detailed description.
    - welcomeMessage (str, optional): Initial greeting.
    - systemPrompt (str): Base instructions for the LLM.
    - responseSettings (object): Configuration for tone, verbosity, creativity, model, release_type, response_length, language.
    - role (str): choose a role for LLM.
    - keywords_list (List[str]): Keywords for RAG retrieval.
    - exception_words (List[str]): Words to exclude.
    - indices (List[str]): Vector or text indices to query.
    - files (List[str]): Local file references.
    """
    return service.create_agent(payload)


@router.get(
    "",
    response_model=List[AgentOut],
    summary="List AI Agents",
    description="Retrieve a paginated list of agents, including all their metadata and settings.",
    responses={
        200: {
            "description": "A list of agents.",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "name": "Support Bot",
                            "description": "Helps with software issues",
                            "welcomeMessage": "Hello!",
                            "systemPrompt": "You are a helpful assistant.",
                            "responseSettings": {
                                "tone": "professional",
                                "verbosity": "detailed",
                                "creativity": 0.7,
                                "model": "gpt-4o",
                                "release_type": "stable",
                                "response_length": "medium",
                                "language": "en"
                            },
                            "role": "دستیار هوشمند",
                            "keywords_list": ["support", "troubleshoot"],
                            "exception_words": ["error", "fail"],
                            "indices": ["index1", "index2"],
                            "files": ["script.py", "notebook.ipynb"],
                            "created_at": "2025-05-07T12:00:00Z",
                            "updated_at": "2025-05-07T12:00:00Z"
                        }
                    ]
                }
            }
        }
    }
)
def list_agents(
    size: int = 10,
    from_: int = 0,
    service: AgentService = Depends(get_agent_service)
):
    """
    - **size**: maximum number of agents to return  
    - **from_**: pagination offset  
    """
    return service.list_agents(size=size, from_=from_)


@router.get(
    "/{agent_id}",
    response_model=AgentOut,
    summary="Get agent details",
    description="Retrieve full details of a single agent by its UUID.",
    responses={
        200: {
            "description": "Agent found",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "name": "Support Bot",
                        "description": "Helps with software issues",
                        "welcomeMessage": "Hello!",
                        "systemPrompt": "You are a helpful assistant.",
                        "responseSettings": {
                            "tone": "professional",
                            "verbosity": "detailed",
                            "creativity": 0.7,
                            "model": "gpt-4o",
                            "release_type": "stable",
                            "response_length": "medium",
                            "language": "en"
                        },
                        "role": "دستیار هوشمند",
                        "keywords_list": ["support", "troubleshoot"],
                        "exception_words": ["error", "fail"],
                        "indices": ["index1", "index2"],
                        "files": ["script.py", "notebook.ipynb"],
                        "created_at": "2025-05-07T12:00:00Z",
                        "updated_at": "2025-05-07T12:00:00Z"
                    }
                }
            }
        },
        404: {"description": "Agent not found"}
    }
)
def get_agent(
    agent_id: str,
    service: AgentService = Depends(get_agent_service)
):
    """
    - **agent_id**: UUID of the agent to retrieve  
    """
    agent = service.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.put(
    "/{agent_id}",
    response_model=AgentOut,
    summary="Update an existing AI Agent",
    description="""
    Update one or more properties of an agent. You may provide any subset of:
    - description  
    - welcomeMessage  
    - systemPrompt  
    - responseSettings (tone, verbosity, creativity, model, release_type, response_length, language)  
    - role
    - keywords_list  
    - exception_words  
    - indices  
    - files  
    """,
    responses={
        200: {"description": "Agent successfully updated"},
        404: {"description": "Agent not found"}
    }
)
def update_agent(
    agent_id: str,
    payload: AgentUpdate,
    service: AgentService = Depends(get_agent_service)
):
    """
    - **agent_id**: UUID of the agent to update  
    - **payload**: fields to modify  
    """
    agent = service.update_agent(agent_id, payload)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.delete(
    "/{agent_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an AI Agent",
    description="Remove an agent and all its associated data from the system.",
    responses={
        204: {"description": "Agent successfully deleted"},
        404: {"description": "Agent not found"}
    }
)
def delete_agent(
    agent_id: str,
    service: AgentService = Depends(get_agent_service)
):
    """
    - **agent_id**: UUID of the agent to delete  
    """
    ok = service.delete_agent(agent_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Agent not found")
    return