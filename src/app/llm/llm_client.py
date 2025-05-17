from openai import OpenAI
from typing import List, Optional, Union, Dict, Any, AsyncGenerator
import json
import logging

logger = logging.getLogger(__name__)
######################################## LLM v1 ######################################
def llm(prompt, llm_model_name = "gpt-4o-mini"):
    base_url = 'https://api.avalai.ir/v1'
    api_key = "aa-gH48KCQ475w3ffeBXXRweoiKcwZORnwxoYYBEjsWOp8nOY93" # aa-...
    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
    )
    message = [
        {"role": "system", "content": "system message"},
        {"role": "user", "content": prompt},
    ]
    response = client.chat.completions.create(
        model=llm_model_name,
        messages=message,
    )

    result = response.choices[0].message.content
    return 200, "successful", result



######################################## LLM v2 ######################################
from openai import (
    AsyncOpenAI,
    APIError,
    APIConnectionError,    RateLimitError,
    AuthenticationError,
    BadRequestError
)
import json # برای استفاده در مثال
from app.api.v1.schemas.llm_result import LLMCallResult

async def llm_async(
    # ورودی محتوا: یا لیست messages یا prompt + system_message
    messages: Optional[List[Dict[str, str]]] = None,
    prompt: Optional[str] = None,    
    system_message: str = "شما یک دستیار هوشمند هستید که باید بر اساس ورودی کاربر پاسخ مناسب ارائه دهید.",

    # تنظیمات مدل و API
    llm_model_name: str = "gpt-4o-mini",  # مدل پیش‌فرض شما
    api_key: Optional[str] = None, # "aa-..." مقدار پیش‌فرض شما بود، بهتر است از config خوانده شود
    base_url: Optional[str] = "https://api.avalai.ir/v1", # base_url پیش‌فرض شما

    # پارامترهای اصلی LLM
    temperature: float = 0.7,
    max_tokens: Optional[int] = 2048, # افزایش مقدار پیش‌فرض برای JSONهای طولانی‌تر    
    top_p: float = 1.0,
    n: int = 1,  # تعداد پاسخ‌های مورد نظر
    stop: Optional[Union[str, List[str]]] = None,
    frequency_penalty: float = 0.0,
    presence_penalty: float = 0.0,    
    seed: Optional[int] = None,  # برای نتایج قابل تکرار
    response_format: Optional[Dict[str, str]] = None,  # مثال: {"type": "json_object"}

    # Streaming
    stream: bool = False,
    stream_options: Optional[Dict[str, Any]] = None, # مثال: {"include_usage": True} برای دریافت usage در stream

    # تنظیمات کلاینت و درخواست
    timeout: Optional[float] = 180.0,  # زمان وقفه برای درخواست API (ثانیه)

    # کنترل خروجی
    return_full_response_dict: bool = True  # اگر stream نباشد، آیا دیکشنری کامل پاسخ API برگردانده شود
    ) -> LLMCallResult:    
    """
    یک تابع پیشرفته و جامع ناهمگام (asynchronous) برای فراخوانی مدل‌های زبان بزرگ (LLM)
    سازگار با OpenAI API.

    نکات:
    - `api_key` و `base_url`: بهتر است این مقادیر از یک سیستم پیکربندی مرکزی (مانند settings در پروژه شما)
      تامین شوند، اما برای انعطاف‌پذیری به عنوان پارامتر نیز پذیرفته می‌شوند.
    - Streaming با `n > 1`: در حالت stream، این تابع به طور پیش‌فرض فقط محتوای اولین choice را stream می‌کند.
      پردازش stream برای چندین choice به طور همزمان پیچیده‌تر است.
    - `max_tokens`: اگر `None` باشد، مدل از مقدار پیش‌فرض خود استفاده می‌کند.
    """
    if not api_key: # یا بررسی کنید که مقدار placeholder نباشد
        logger.error("کلید API (api_key) پیکربندی نشده است.")
        return LLMCallResult(success=False, status_code=401, message="خطای پیکربندی", error_detail="کلید API تعریف نشده است.")

    if not messages and not prompt:
        logger.error("باید پارامتر 'messages' یا 'prompt' ارائه شود.")
        return LLMCallResult(success=False, status_code=400, message="خطای ورودی", error_detail="هیچ ورودی ارائه نشده است.")

    if messages and prompt:
        logger.warning("هر دو پارامتر 'messages' و 'prompt' ارائه شده‌اند. از 'messages' استفاده خواهد شد.")

    actual_messages: List[Dict[str, str]]
    if messages:
        actual_messages = messages
    else:
        actual_messages = [{"role": "system", "content": system_message}]
        if prompt: # به دلیل بررسی قبلی، اگر messages نباشد، prompt حتما وجود دارد
            actual_messages.append({"role": "user", "content": prompt})
        else: # این حالت نباید رخ دهد، اما برای اطمینان
            return LLMCallResult(success=False, status_code=400, message="خطای ورودی", error_detail="Prompt خالی است.")

    try:        
        client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout
        )

        request_params = {
            "model": llm_model_name,
            "messages": actual_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "n": n,
            "stop": stop,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
            "seed": seed,
            "stream": stream,
        }        
        if response_format:
            request_params["response_format"] = response_format
        if stream and stream_options:
            request_params["stream_options"] = stream_options
        
        # حذف کلیدهایی با مقدار None اگر API به آنها حساس است (معمولاً کلاینت OpenAI مدیریت می‌کند)
        # request_params = {k: v for k, v in request_params.items() if v is not None}


        logger.info(f"ارسال درخواست به LLM: model={llm_model_name}, stream={stream}, تعداد پیام‌ها={len(actual_messages)}")
        # در محیط عملیاتی، لاگ کردن کامل پیام‌ها (prompt) باید با احتیاط انجام شود.
        # logger.debug(f"پارامترهای درخواست LLM: {request_params}")

        completion = await client.chat.completions.create(**request_params) # type: ignore

        if stream:
            async def stream_generator() -> AsyncGenerator[str, None, None]:
                accumulated_content = ""
                usage_from_stream = None
                try:
                    async for chunk in completion: # type: ignore
                        if stream_options and stream_options.get("include_usage") and hasattr(chunk, 'usage') and chunk.usage:
                            usage_from_stream = chunk.usage.model_dump()
                            # logger.debug(f"اطلاعات Usage از stream دریافت شد: {usage_from_stream}")
                            # توجه: اطلاعات usage معمولا در آخرین chunk می‌آید.
                            # این تابع ژنراتور فقط رشته‌های محتوا را yield می‌کند،
                            # بنابراین usage باید توسط مصرف‌کننده ژنراتور جداگانه بررسی شود یا پس از اتمام استریم.

                        if chunk.choices:
                            content_delta = chunk.choices[0].delta.content
                            if content_delta:
                                accumulated_content += content_delta                                
                                yield content_delta

                    # logger.debug(f"محتوای کامل stream شده (اولیه): {accumulated_content[:200]}")
                except Exception as e_stream:
                    logger.error(f"خطا در حین پردازش stream از LLM: {e_stream}", exc_info=True)
                    raise # خطا مجددا ارسال می‌شود تا توسط مصرف‌کننده ژنراتور مدیریت شود

            logger.info("فراخوانی LLM موفقیت‌آمیز بود، پاسخ به صورت stream ارائه می‌شود.")
            # برای سادگی، اطلاعات usage مستقیماً از طریق LLMCallResult برای stream برگردانده نمی‌شود.            # مصرف‌کننده می‌تواند آخرین chunk را برای usage بررسی کند اگر stream_options فعال باشد.
            return LLMCallResult(success=True, status_code=200, message="Streaming آغاز شد", stream_data=stream_generator())

        else:  # حالت غیر stream
            usage_data = completion.usage.model_dump() if completion.usage else None
            logger.info(f"فراخوانی LLM موفقیت‌آمیز بود. Usage: {usage_data}")

            if return_full_response_dict:
                return LLMCallResult(success=True, status_code=200, message="موفقیت‌آمیز",
                                     full_response_data=completion.model_dump(), usage=usage_data)
            else:
                if n == 1 and completion.choices:
                    content_result = completion.choices[0].message.content
                elif n > 1 and completion.choices:
                    content_result = [choice.message.content for choice in completion.choices if choice.message and choice.message.content is not None]
                else:
                    content_result = None # یا یک رشته خالی اگر هیچ محتوایی وجود نداشت
                    if not completion.choices:
                         logger.warning("پاسخ LLM شامل هیچ choice ای نبود.")


                return LLMCallResult(success=True, status_code=200, message="موفقیت‌آمیز",
                                     content=content_result, usage=usage_data)

    except APIConnectionError as e:
        logger.error(f"خطای اتصال به OpenAI API: {e}", exc_info=True)
        return LLMCallResult(success=False, status_code=getattr(e, 'status_code', 503), message="خطای اتصال به API", error_detail=str(e))
    except RateLimitError as e:
        logger.error(f"خطای محدودیت تعداد درخواست (Rate Limit) OpenAI API: {e}", exc_info=True)
        return LLMCallResult(success=False, status_code=getattr(e, 'status_code', 429), message="محدودیت تعداد درخواست", error_detail=str(e))
    except AuthenticationError as e:
        logger.error(f"خطای احراز هویت OpenAI API: {e}", exc_info=True)
        return LLMCallResult(success=False, status_code=getattr(e, 'status_code', 401), message="خطای احراز هویت", error_detail=str(e))
    except BadRequestError as e: # شامل مواردی مانند مدل نامعتبر، طول زمینه بیش از حد و ...
        logger.error(f"خطای درخواست نامعتبر (Bad Request) OpenAI API: {e}", exc_info=True)
        return LLMCallResult(success=False, status_code=getattr(e, 'status_code', 400), message="درخواست نامعتبر", error_detail=str(e))
    except APIError as e:  # خطای عمومی OpenAI API
        logger.error(f"خطای OpenAI API: {e}", exc_info=True)
        return LLMCallResult(success=False, status_code=getattr(e, 'status_code', 500), message="خطای API", error_detail=str(e))
    except Exception as e:  # گرفتن سایر خطاهای پیش‌بینی نشده
        logger.error(f"یک خطای پیش‌بینی نشده رخ داد: {e}", exc_info=True)
        return LLMCallResult(success=False, status_code=500, message="خطای پیش‌بینی نشده", error_detail=str(e))





##########################################
async def llm_async(
    # ورودی محتوا: یا لیست messages یا prompt + system_message
    messages: Optional[List[Dict[str, str]]] = None,
    prompt: Optional[str] = None,    
    system_message: str = "شما یک دستیار هوشمند هستید که باید بر اساس ورودی کاربر پاسخ مناسب ارائه دهید.",

    # تنظیمات مدل و API
    llm_model_name: str = "gpt-4o-mini",  # مدل پیش‌فرض شما
    api_key: Optional[str] = None, # "aa-..." مقدار پیش‌فرض شما بود، بهتر است از config خوانده شود
    base_url: Optional[str] = "https://api.avalai.ir/v1", # base_url پیش‌فرض شما

    # پارامترهای اصلی LLM
    temperature: float = 0.7,
    max_tokens: Optional[int] = 2048, # افزایش مقدار پیش‌فرض برای JSONهای طولانی‌تر    
    top_p: float = 1.0,
    n: int = 1,  # تعداد پاسخ‌های مورد نظر
    stop: Optional[Union[str, List[str]]] = None,
    frequency_penalty: float = 0.0,
    presence_penalty: float = 0.0,    
    seed: Optional[int] = None,  # برای نتایج قابل تکرار
    response_format: Optional[Dict[str, str]] = None,  # مثال: {"type": "json_object"}

    # Streaming
    stream: bool = False,
    stream_options: Optional[Dict[str, Any]] = None, # مثال: {"include_usage": True} برای دریافت usage در stream

    # تنظیمات کلاینت و درخواست
    timeout: Optional[float] = 90.0,  # زمان وقفه برای درخواست API (ثانیه)

    # کنترل خروجی
    return_full_response_dict: bool = True  # اگر stream نباشد، آیا دیکشنری کامل پاسخ API برگردانده شود
) -> "LLMCallResult":
    """
    یک تابع پیشرفته و جامع ناهمگام (asynchronous) برای فراخوانی مدل‌های زبان بزرگ (LLM)
    سازگار با OpenAI API.

    نکات:
    - `api_key` و `base_url`: بهتر است این مقادیر از یک سیستم پیکربندی مرکزی (مانند settings در پروژه شما)
      تامین شوند، اما برای انعطاف‌پذیری به عنوان پارامتر نیز پذیرفته می‌شوند.
    - Streaming با `n > 1`: در حالت stream، این تابع به طور پیش‌فرض فقط محتوای اولین choice را stream می‌کند.
      پردازش stream برای چندین choice به طور همزمان پیچیده‌تر است.
    - `max_tokens`: اگر `None` باشد، مدل از مقدار پیش‌فرض خود استفاده می‌کند.
    """
    # ۱. ولیدیت کلید API
    if not api_key:
        logger.error("کلید API (api_key) پیکربندی نشده است.")
        return LLMCallResult(
            success=False,
            status_code=401,
            message="خطای پیکربندی",
            error_detail="کلید API تعریف نشده است."
        )

    # ۲. ولیدیت ورودی پیام یا پرامپت
    if not messages and not prompt:
        logger.error("باید پارامتر 'messages' یا 'prompt' ارائه شود.")
        return LLMCallResult(
            success=False,
            status_code=400,
            message="خطای ورودی",
            error_detail="هیچ ورودی ارائه نشده است."
        )
    if messages and prompt:
        logger.warning(
            "هر دو پارامتر 'messages' و 'prompt' ارائه شده‌اند. از 'messages' استفاده خواهد شد."
        )

    # ۳. تنظیم actual_messages
    if messages:
        actual_messages = messages
    else:
        actual_messages = [{"role": "system", "content": system_message}]
        actual_messages.append({"role": "user", "content": prompt or ""})

    try:
        # ۴. ساخت کلاینت ناهمگام
        client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout
        )

        # ۵. آماده‌سازی پارامترهای درخواست
        request_params: Dict[str, Any] = {
            "model": llm_model_name,
            "messages": actual_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "n": n,
            "stop": stop,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
            "seed": seed,
            "stream": stream,
        }
        if response_format:
            request_params["response_format"] = response_format
        if stream and stream_options:
            request_params["stream_options"] = stream_options

        logger.info(
            f"ارسال درخواست به LLM: model={llm_model_name}, stream={stream}, "
            f"messages={len(actual_messages)}"
        )

        # ۶. فراخوانی API
        completion = await client.chat.completions.create(**request_params)  # type: ignore

        # ۷. حالت stream
        if stream:
            async def stream_generator() -> AsyncGenerator[str, None]:
                try:
                    async for chunk in completion:  # type: ignore
                        # استخراج دلتا
                        delta = chunk.choices[0].delta.content
                        if delta:
                            yield delta
                except Exception as e_stream:
                    logger.error(
                        f"خطا در حین پردازش stream از LLM: {e_stream}",
                        exc_info=True
                    )
                    raise

            logger.info("Streaming response ready.")
            return LLMCallResult(
                success=True,
                status_code=200,
                message="Streaming آغاز شد",
                stream_data=stream_generator()
            )

        # ۸. حالت non-stream
        usage_data = None
        if getattr(completion, "usage", None):
            usage_data = completion.usage.model_dump()

        logger.info(f"LLM call succeeded. Usage: {usage_data}")

        if return_full_response_dict:
            return LLMCallResult(
                success=True,
                status_code=200,
                message="موفقیت‌آمیز",
                full_response_data=completion.model_dump(),
                usage=usage_data
            )

        # استخراج محتوا براساس n
        if n == 1 and completion.choices:
            content_result = completion.choices[0].message.content
        else:
            content_result = [
                c.message.content
                for c in completion.choices
                if c.message and c.message.content is not None
            ]

        return LLMCallResult(
            success=True,
            status_code=200,
            message="موفقیت‌آمیز",
            content=content_result,
            usage=usage_data
        )

    # ۹. هندل کردن خطاهای مختلف OpenAI
    except APIConnectionError as e:
        logger.error(f"خطای اتصال به OpenAI API: {e}", exc_info=True)
        return LLMCallResult(
            success=False,
            status_code=503,
            message="خطای اتصال به API",
            error_detail=str(e)
        )
    except RateLimitError as e:
        logger.error(f"Rate limit error: {e}", exc_info=True)
        return LLMCallResult(
            success=False,
            status_code=429,
            message="محدودیت تعداد درخواست",
            error_detail=str(e)
        )
    except AuthenticationError as e:
        logger.error(f"Authentication error: {e}", exc_info=True)
        return LLMCallResult(
            success=False,
            status_code=401,
            message="خطای احراز هویت",
            error_detail=str(e)
        )
    except BadRequestError as e:
        logger.error(f"Bad request: {e}", exc_info=True)
        return LLMCallResult(
            success=False,
            status_code=400,
            message="درخواست نامعتبر",
            error_detail=str(e)
        )
    except APIError as e:
        logger.error(f"OpenAI API error: {e}", exc_info=True)
        return LLMCallResult(
            success=False,
            status_code=500,
            message="خطای API",
            error_detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return LLMCallResult(
            success=False,
            status_code=500,
            message="خطای پیش‌بینی نشده",
            error_detail=str(e)
        )