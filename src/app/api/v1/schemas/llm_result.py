import logging
from typing import List, Optional, Union, Dict, Any, AsyncGenerator

# یک لاگر برای این ماژول تنظیم می‌کنیم
logger = logging.getLogger(__name__)

class LLMCallResult:
    def __init__(self,
                 success: bool,
                 status_code: Optional[int] = None,  # کد وضعیت HTTP-مانند در صورت وجود
                 message: Optional[str] = None,      # پیام کلی (موفقیت آمیز، خطا و ...)
                 content: Optional[Union[str, List[str]]] = None,  # محتوای اصلی پاسخ (رشته یا لیست رشته‌ها برای n>1)
                 full_response_data: Optional[Dict[str, Any]] = None,  # دیکشنری کامل پاسخ API (در صورت درخواست)
                 stream_data: Optional[AsyncGenerator[str, None]] = None,  # ژنراتور برای حالت stream
                 error_detail: Optional[str] = None, # جزئیات خطا
                 usage: Optional[Dict[str, Any]] = None):  # اطلاعات مصرف توکن (usage)
        self.success = success
        self.status_code = status_code
        self.message = message        
        self.content = content
        self.full_response_data = full_response_data
        self.stream_data = stream_data
        self.error_detail = error_detail
        self.usage = usage

    def __repr__(self):
        return (f"LLMCallResult(success={self.success}, status_code={self.status_code}, "
                f"message='{self.message}', error_detail='{self.error_detail}', "
                f"has_content={self.content is not None}, "
                f"has_full_response={self.full_response_data is not None}, "
                f"is_streaming={self.stream_data is not None}, "
                f"usage={self.usage})")