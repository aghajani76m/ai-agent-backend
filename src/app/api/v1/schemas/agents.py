from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class ResponseSettings(BaseModel):
    tone: Optional[str]      = Field("neutral", example="professional")
    verbosity: Optional[str] = Field("medium", example="detailed")
    creativity: Optional[float] = Field(0.5, example=0.7)
    model: Optional[str]     = Field("gpt-4o-mini", example="gpt-4o-mini")

class AgentCreate(BaseModel):
    name: str = Field(..., example="sales-assistant")
    description: Optional[str] = Field(None, example="Handles sales inquiries")
    welcomeMessage: Optional[str] = Field(None, example="Hello! How can I help you?")
    systemPrompt: str = Field(None, example="You are a helpful sales assistant.")
    responseSettings: ResponseSettings = Field(
        default_factory=ResponseSettings
    )

class AgentUpdate(BaseModel):
    description: Optional[str] = Field(None, example="Updated description for the assistant")
    welcomeMessage: Optional[str] = Field(None, example="Welcome back! How may I assist you?")
    systemPrompt: Optional[str] = Field(None, example="You are a polite and helpful assistant.")
    responseSettings: ResponseSettings = Field(
        default_factory=ResponseSettings
    )

class AgentOut(BaseModel):
    id: str = Field(..., example="uuid-of-agent")
    name: str = Field(..., example="sales-assistant")
    description: Optional[str] = Field(None, example="Handles sales inquiries")
    welcomeMessage: Optional[str] = Field(None, example="Hello! How can I help you?")
    systemPrompt: str = Field(..., example="You are a helpful sales assistant.")
    responseSettings: ResponseSettings = Field(
        default_factory=ResponseSettings
    )
    class Config:
        orm_mode = True

class AgentBase(BaseModel):
    name: str = Field(..., example="sales-assistant")
    description: Optional[str] = Field(None, example="Handles sales inquiries")
    welcomeMessage: Optional[str] = Field(None, example="Hello! How can I help you?")
    systemPrompt: Optional[str] = Field(None, example="You are a helpful sales assistant.")
    responseSettings: ResponseSettings = Field(
        default_factory=ResponseSettings
    )

class AgentInDB(AgentBase):
    id: str = Field(..., example="uuid-of-agent")
    created_at: datetime = Field(..., example="2024-10-10T15:45:00")
