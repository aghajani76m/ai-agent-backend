# POST /conversations
# POST /conversations/{conv_id}/messages
# GET /conversations
# GET /conversations/{conv_id}
# GET /conversations/{conv_id}/messages
# GET /conversations/{conv_id}/tokens

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from minio import Minio
from elasticsearch import Elasticsearch

from app.api.v1.schemas.conversation import (
    ConversationCreate, ConversationOut, ConversationWithMessages,
    MessageCreate, MessageOut
)
from app.services.conversation_service import ConversationService
from app.services.agent_es_service import AgentService
from app.core.dependencies import get_es_client, get_llm_client, get_minio_client
from app.services.file_service import FileService

router = APIRouter(prefix="/conversations", tags=["conversations"])


def get_agent_svc(es: Elasticsearch = Depends(get_es_client)) -> AgentService:
    return AgentService(es)


def get_file_service(minio_client: Minio = Depends(get_minio_client)):
    return FileService(minio_client)


def get_conv_service(
    es=Depends(get_es_client),
    llm=Depends(get_llm_client),
    agent_svc=Depends(get_agent_svc),
    file_svc: FileService = Depends(get_file_service)
):
    return ConversationService(es, llm, agent_svc, file_svc)


@router.post(
    "",
    response_model=ConversationOut,
    status_code=status.HTTP_201_CREATED,
    summary="Start a new conversation",
    description="Initiate a new conversation for a specific agent.",
    responses={
        201: {
            "description": "Conversation created",
            "content": {
                "application/json": {
                    "example": {
                        "id": "conv-abc123",
                        "agent_id": "123e4567-e89b-12d3-a456-426614174000",
                        "started_at": "2025-05-07T12:00:00Z"
                    }
                }
            }
        }
    }
)
def create_conversation(
    payload: ConversationCreate,
    svc: ConversationService = Depends(get_conv_service)
):
    """
    - **agent_id**: UUID of the agent to chat with  
    """
    conv = svc.create_conversation(payload)
    return conv


@router.post(
    "/{conv_id}/messages",
    response_model=ConversationWithMessages,
    status_code=status.HTTP_201_CREATED,
    summary="Send a message and receive LLM response",
    description="Add a user message to the conversation, call the LLM, and return the updated history.",
    responses={
        201: {"description": "Message posted and assistant replied"},
        404: {"description": "Conversation or Agent not found"}
    }
)
def post_message(
    conv_id: str,
    payload: MessageCreate,
    svc: ConversationService = Depends(get_conv_service)
):
    """
    - **conv_id**: ID of the conversation  
    - **content**: user message text  
    - **attachments**: optional file attachments  
    """
    convo = svc.send_message(conv_id, payload)
    if convo is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Conversation or Agent not found")
    return convo


@router.get(
    "",
    response_model=List[ConversationOut],
    summary="List conversations",
    description="Retrieve a paginated list of conversations across all agents.",
    responses={200: {"description": "A list of conversations"}}
)
def list_conversations(
    size: int = 10,
    from_: int = 0,
    svc: ConversationService = Depends(get_conv_service)
):
    """
    - **size**: number of conversations to return  
    - **from_**: pagination offset  
    """
    return svc.list_conversations(size=size, from_=from_)


@router.get(
    "/{conv_id}",
    response_model=ConversationWithMessages,
    summary="Get conversation with full history",
    description="Retrieve a conversation and all its messages.",
    responses={
        200: {"description": "Conversation returned"},
        404: {"description": "Conversation not found"}
    }
)
def get_conversation(
    conv_id: str,
    svc: ConversationService = Depends(get_conv_service)
):
    """
    - **conv_id**: ID of the conversation to fetch  
    """
    conv = svc.get_conversation(conv_id)
    if not conv:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Conversation not found")
    msgs = svc.list_messages(conv_id)
    return ConversationWithMessages(**conv.dict(), messages=msgs)


@router.get(
    "/{conv_id}/messages",
    response_model=List[MessageOut],
    summary="List messages in a conversation",
    description="Retrieve only the messages for the given conversation.",
    responses={200: {"description": "List of messages"}}
)
def list_messages(
    conv_id: str,
    svc: ConversationService = Depends(get_conv_service)
):
    """
    - **conv_id**: ID of the conversation  
    """
    return svc.list_messages(conv_id)


@router.get(
    "/{conv_id}/tokens",
    summary="Get total token usage",
    description="Return total prompt, completion, and combined token usage for a conversation.",
    responses={
        200: {
            "description": "Token usage summary",
            "content": {
                "application/json": {
                    "example": {
                        "total_tokens": 200
                    }
                }
            }
        },
        404: {"description": "Conversation not found"}
    }
)
def token_calculator(
    conv_id: str,
    svc: ConversationService = Depends(get_conv_service)
):
    """
    - **conv_id**: ID of the conversation  
    """
    conv = svc.get_conversation(conv_id)
    if not conv:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Conversation not found")
    total_tokens_usage = svc.total_token_usage(conv_id)
    return total_tokens_usage