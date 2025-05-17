from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

# ---- Conversation ----
# class TokenUsage(BaseModel):
#     prompt_tokens: int
#     completion_tokens: int
#     total_tokens: int

class FileAttachment(BaseModel):
    id: str = Field(..., example="file-uuid")
    filename: str = Field(..., example="report.pdf")
    url: str = Field(..., example="https://example.com/files/report.pdf")

class ConversationCreate(BaseModel):
    agent_id: str = Field(..., example="uuid-of-agent")
    title: Optional[str] = Field(None, example="Sales Chat #1")

class ConversationInDB(BaseModel):
    id: str = Field(..., example="uuid-of-conversation")
    agent_id: str = Field(..., example="uuid-of-agent")
    title: Optional[str] = Field(None, example="Sales Chat #1")
    created_at: datetime = Field(..., example="2024-10-10T14:30:00")

class ConversationOut(ConversationInDB):
    pass

# ---- Message ----
class MessageBase(BaseModel):
    role: str = Field(..., example="user")  # or "assistant" or "system"
    content: str = Field(..., example="Hello, I need help.")

class MessageCreate(BaseModel):
    content: str = Field(..., example="Let's start talking... What's up?!")
    attachments: Optional[List[FileAttachment]] = Field(
        default_factory=list,
        example=[{"id":"uuid","filename":"invoice.pdf","url":"http://example.com/files/invoice.pdf"}]
    )

class MessageInDB(BaseModel):
    id: str = Field(..., example="uuid-of-message")
    conversation_id: str = Field(..., example="uuid-of-conversation")
    role: str = Field(..., example="assistant")
    content: str = Field(..., example="Sure! I can help with that.")
    attachments: List[FileAttachment] = Field(default_factory=list)
    created_at: datetime = Field(..., example="2024-10-10T14:31:00")
    token_usage: Optional[int] = Field(0, example=56)

class MessageOut(MessageInDB):
    pass

class ConversationWithMessages(ConversationOut):
    messages: List[MessageOut] = Field(default_factory=list)
