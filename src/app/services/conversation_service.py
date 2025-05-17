import uuid
from datetime import datetime
from typing import List, Optional, Dict

from elasticsearch import Elasticsearch, NotFoundError
import openai
import time
from app.api.v1.schemas.conversation import (
    ConversationCreate, ConversationInDB, ConversationOut, ConversationWithMessages,
    MessageCreate, MessageInDB, MessageOut
)
from app.services.file_service import FileService
from app.services.agent_es_service import AgentService
from app.core.dependencies import get_es_client

# ایندکس‌ها
CONV_INDEX = "conversations"
MSG_INDEX  = "messages"

class ConversationService:
    def __init__(self, es, llm_client, agent_svc: AgentService, file_svc: FileService):
        self.es = es
        self.llm = llm_client
        self.agent_svc = agent_svc
        self.file_svc = file_svc

    # 1. Conversation CRUD
    def create_conversation(self, data: ConversationCreate) -> ConversationInDB:
        conv_id = str(uuid.uuid4())
        now = datetime.utcnow()
        doc = {"agent_id": data.agent_id, "title": data.title, "created_at": now}
        self.es.index(index=CONV_INDEX, id=conv_id, document=doc)
        return ConversationInDB(id=conv_id, **doc)

    def get_conversation(self, conv_id: str) -> Optional[ConversationOut]:
        try:
            res = self.es.get(index=CONV_INDEX, id=conv_id)
        except NotFoundError:
            return None
        src = res["_source"]
        return ConversationOut(id=res["_id"], **src)

    def list_conversations(self, size: int=10, from_: int=0) -> List[ConversationOut]:
        res = self.es.search(
            index=CONV_INDEX,
            body={"from": from_, "size": size, "sort":[{"created_at":{"order":"desc"}}]}
        )
        out = []
        for h in res["hits"]["hits"]:
            src = h["_source"]
            out.append(ConversationOut(id=h["_id"], **src))
        return out

    # 2. Message CRUD + LLM
    def list_messages(self, conv_id: str, size:int=100, from_:int=0) -> List[MessageOut]:
        res = self.es.search(
            index=MSG_INDEX,
            body={
                "query": {"term": {"conversation_id": conv_id}},
                "sort": [{"created_at": {"order": "asc"}}],
                "from": from_, "size": size
            }
        )
        msgs = []
        for h in res["hits"]["hits"]:
            src = h["_source"]
            msgs.append(MessageOut(id=h["_id"], **src))
        return msgs
    
    def token_calculator(self, content):
        return int(len(content)/2)

    def _index_message(
        self,
        conv_id: str,
        role: str,
        content: str,
        attachments: Optional[List[Dict]] = None,
        token_usage: int = 0
    ) -> MessageInDB:
        """
        ایندکس یک پیام در ES به همراه ضمیمه‌ها (در صورت وجود).
        attachments: لیستی از dictهای {"id","filename","url"}.
        """
        msg_id = str(uuid.uuid4())
        now = datetime.utcnow()
        atts = attachments or []

        doc = {
            "conversation_id": conv_id,
            "role": role,
            "content": content,
            "attachments": atts,
            "created_at": now,
            "token_usage": token_usage
        }
        self.es.index(index=MSG_INDEX, id=msg_id, document=doc)
        return MessageInDB(id=msg_id, **doc)
            
    def send_message(
        self, conv_id: str, user_msg: MessageCreate
    ) -> ConversationWithMessages:
        """
        1) ایندکس پیام کاربر به همراه attachments
        2) ساخت prompt با system + history + user+attachments
        3) فراخوانی LLM واسط شما
        4) ایندکس پاسخ Assistant
        5) بازیابی و برگرداندن کل مکالمه
        """
        # 1) آماده‌سازی لیست ضمیمه‌ها با presigned URL
        atts_for_index: List[Dict] = []
        for a in user_msg.attachments or []:
            # a.id, a.filename
            url = self.file_svc.get_presigned_url(a.id, a.filename)
            atts_for_index.append({
                "id": a.id,
                "filename": a.filename,
                "url": url,
            })
        # محاسبه توکن
        token_usage = self.token_calculator(user_msg.content) or 0
        # ذخیره پیام کاربر
        self._index_message(conv_id, "user", user_msg.content, atts_for_index, token_usage)

        # بارگذاری conversation و agent
        conv = self.get_conversation(conv_id)
        if not conv:
            return None
        agent = self.agent_svc.get_agent(conv.agent_id)
        if not agent:
            return None

        # 2) ساخت prompt
        parts: List[str] = []

        # system prompt اگر وجود دارد
        if getattr(agent, "systemPrompt", None):
            parts.append(f"SYSTEM: {agent.systemPrompt}")

        # تاریخچه پیام‌ها
        history: List[MessageOut] = self.list_messages(conv_id)
        for m in history:
            parts.append(f"{m.role.upper()}: {m.content}")
            # اگر ضمیمه‌ای داشته باشند، در prompt اعلام می‌کنیم
            for att in m.attachments or []:
                parts.append(f"[Attachment: {att.filename} -> {att.url}]")

        # پیام جدید کاربر
        parts.append(f"USER: {user_msg.content}")
        for att in atts_for_index:
            parts.append(f"[Attachment: {att['filename']} -> {att['url']}]")

        prompt_text = "\n".join(parts)
        # 3) فراخوانی LLM واسط
        model_name = agent.responseSettings.model or "gpt-4o-mini"
        code, status_msg, assistant_text = self.llm(prompt_text, model_name)
        # جمع توکن ورودی پرامپت و خروجی مدل
        token_usage = (self.token_calculator(prompt_text) or 0) + (self.token_calculator(assistant_text) or 0)
        # 4) ایندکس پاسخ
        self._index_message(conv_id, "assistant", assistant_text, [], token_usage)

        # (اختیاری) کمی تأخیر برای همگام‌سازی
        time.sleep(2)

        # 5) بازگرداندن کل مکالمه
        msgs = self.list_messages(conv_id)
        return ConversationWithMessages(**conv.dict(), messages=msgs)

    def total_token_usage(self, conv_id: str) -> int:
        res = self.es.search(
            index=MSG_INDEX,
            body={
                "size": 0,  # نیازی به برگرداندن داکیومنت نیست
                "query": {
                    "term": {"conversation_id": conv_id}
                },
                "aggs": {
                    "total_tokens": {
                        "sum": {
                            "field": "token_usage"
                        }
                    }
                }
            }
        )
        return int(res["aggregations"]["total_tokens"]["value"] or 0)
