from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum
from typing import Any, Dict, List, Optional

#
# 1) محدودسازی انتخاب‌ها با Enum
#
class LLMModelName(str, Enum):
    gpt_4o_mini   = "gpt-4o-mini"
    gpt_4o        = "gpt-4o"
    deepseek_chat = "deepseek-chat"
    # اگر خواستید به تنظیمات پیشین بازگردید:
    # OTHER = "other-model-name"

class RoleEnum(str, Enum):
    SMART_ASSISTANT = "دستیار هوشمند"
    DEVELOPER       = "برنامه‌نویس"
    LAWYER          = "حقوقدان"
    TRANSLATOR      = "مترجم"
    PROJECT_MANAGER = "مدیر پروژه"

class ReleaseType(str, Enum):
    private  = "private"
    public   = "public"
    # پیشین:
    # ANY = "any"


class ToneEnum(str, Enum):
    neutral      = "neutral"
    friendly     = "friendly"
    professional = "professional"
    casual       = "casual"
    formal       = "formal"
    # پیشین:
    # tone: Optional[str] = "neutral"


class ResponseLengthEnum(str, Enum):
    short  = "short"
    medium = "medium"
    long   = "long"
    # پیشین:
    # response_length: Optional[str] = "medium"


class LanguageEnum(str, Enum):
    en = "en"
    fa = "fa"
    # es = "es"
    # fr = "fr"
    # پیشین:
    # language: Optional[str] = "en"


class CreativityLevel(float, Enum):
    low    = 0.2
    medium = 0.5
    high   = 0.7
    max    = 1.0
    # پیشین:
    # creativity: Optional[float] = 0.5


#
# 2) مدل پاسخ‌دهی
#
class ResponseSettings(BaseModel):
    # tone: Optional[str]      = Field("neutral", example="professional")
    tone: ToneEnum = Field(
        ToneEnum.neutral,
        example=ToneEnum.professional,
        description="The style/tone of the assistant’s replies",    
        alias="tone"
    )

    # verbosity: Optional[str] = Field("medium", example="detailed")
    # verbosity: str = Field(
    #     "medium",
    #     example="detailed",
    #     description="How verbose/detailed the responses should be"
    # )

    # creativity: Optional[float] = Field(0.5, example=0.7)
    creativity: CreativityLevel = Field(
        CreativityLevel.medium,
        example=CreativityLevel.high,
        description="A float between 0.0 and 1.0 that controls creativity",
        alias="creativity"
    )

    # model: Optional[str]     = Field("gpt-4o-mini", example="gpt-4o-mini")
    model: LLMModelName = Field(
        LLMModelName.gpt_4o_mini,
        example=LLMModelName.gpt_4o,
        description="Which LLM to use for responses",
        alias="llm_model_name"
    )

    # --- افزودن فیلدهای جدید مطابق مپینگ ---
    release_type: ReleaseType = Field(
        ReleaseType.private,
        example=ReleaseType.private,
        description="Release stage of the agent",
        alias="release_type"
    )

    response_length: ResponseLengthEnum = Field(
        ResponseLengthEnum.medium,
        example=ResponseLengthEnum.short,
        description="Length category of the response",
        alias="response_length"
    )

    language: LanguageEnum = Field(
        LanguageEnum.en,
        example=LanguageEnum.fa,
        description="Response language",
        alias="language"
    )


#
# 3) مدل‌های ورودی/خروجی
#
class AgentBase(BaseModel):
    name: str = Field(..., example="sales-assistant")
    description: Optional[str] = Field(
        None, example="Handles sales inquiries",
        alias="description"
    )

    # قبلی => welcomeMessage: Optional[str]
    welcome_message: Optional[str] = Field(
        None,
        alias="welcomeMessage",
        example="Hello! How can I help you?"
    )

    # قبلی => systemPrompt: Optional[str]
    system_prompt: Optional[str] = Field(
        None,
        alias="systemPrompt",
        example="You are a helpful sales assistant."
    )

    response_settings: ResponseSettings = Field(
        default_factory=ResponseSettings,
        alias="response_settings"
    )

    # مطابق مپینگ:
    keywords_list: List[str] = Field(
        default_factory=list,
        alias="keywords_list",
        example=["sales", "support"],
        description="List of keywords associated with this agent"
    )

    exception_words: List[str] = Field(
        default_factory=list,
        alias="exception_words",
        example=["foo", "bar"],
        description="Words to be excluded from certain operations"
    )

    indices: List[str] = Field(
        default_factory=list,
        example=["indexA", "indexB"],
        description="Search indices used by RAG"
    )

    files: List[str] = Field(
        default_factory=list,
        example=["file1.py", "notebook.ipynb"],
        description="List of file paths associated with this agent"
    )

    role: RoleEnum = Field(
        RoleEnum.SMART_ASSISTANT,
        alias="role",
        description="یکی از ۵ نقش مجاز: دستیار هوشمند (default)، برنامه‌نویس، حقوقدان، مترجم، مدیر پروژه"
    )
    
    class Config:
        orm_mode = True
        allow_population_by_field_name = True

class AgentCreate(AgentBase):
    # در Create، id و timestamps نداریم
    pass


class AgentUpdate(BaseModel):
    description: Optional[str] = Field(
        None, example="Updated description for the assistant"
    )
    welcome_message: Optional[str] = Field(
        None,
        alias="welcomeMessage",
        example="Welcome back! How may I assist you?"
    )
    system_prompt: Optional[str] = Field(
        None,
        alias="systemPrompt",
        example="You are a polite and helpful assistant."
    )
    response_settings: Optional[ResponseSettings] = Field(
        None,
        alias="response_settings",
        description="settings of response"
    )
    keywords_list: Optional[List[str]] = Field(
        None, alias="keywords_list", example=["new", "keywords"]
    )
    exception_words: Optional[List[str]] = Field(
        None, alias="exception_words", example=["spam", "ads"]
    )
    indices: Optional[List[str]] = Field(
        None, example=["indexC", "indexD"]
    )
    files: Optional[List[str]] = Field(
        None, example=["module.py", "analysis.ipynb"]
    )


class AgentOut(AgentBase):
    id: str = Field(..., example="uuid-of-agent")
    created_at: datetime = Field(
        ..., example="2024-10-10T15:45:00Z"
    )
    updated_at: datetime = Field(
        ..., example="2024-10-12T08:30:00Z"
    )

    class Config(AgentBase.Config):
        pass


class AgentInDB(AgentBase):
    id: str = Field(..., example="uuid-of-agent")
    created_at: datetime = Field(
        ..., example="2024-10-10T15:45:00Z"
    )
    updated_at: datetime = Field(
        ..., example="2024-10-12T08:30:00Z"
    )
    class Config(AgentBase.Config):
        pass