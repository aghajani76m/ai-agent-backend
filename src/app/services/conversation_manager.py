from .ai_client import AIClient
from app.db.session import SessionLocal

class ConversationManager:
    def __init__(self, db):
        self.db = db
        self.ai = AIClient()

    def start_conversation(self, agent_id: int):
        # ایجاد رکورد Conversation در DB
        # اضافه کردن پیام system (system_prompt)
        # بازگرداندن conversation_id و welcomeMessage
        ...

    def send_message(self, conv_id: int, user_message: str):
        # واکشی تاریخچه پیام‌ها از DB
        # ساخت prompt شامل system + تاریخچه + پیام کاربر
        # فراخوانی OpenAI
        # ذخیره پیام کاربر و پیام assistant با تعداد توکن
        # بازگرداندن پاسخ
        ...