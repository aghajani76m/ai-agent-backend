import openai
import json
import logging
from typing import Tuple, Optional
from app.core.config import settings
from app.llm.prompts.resume import RESUME_PROCESSING_PROMPT_TEMPLATE
from app.llm.llm_client import llm_async
from app.api.v1.schemas.llm_result import LLMCallResult
import logging

logger = logging.getLogger(__name__)


async def process_resume_text(
    resume_text: str,
    input_model: str = "gpt-4o-mini" # gpt-4o
) -> Tuple[Optional[dict], Optional[dict]]:
    """
    Sends resume text to LLM and expects two JSON objects in response:
      { parsedResult: { extractedData:…, extractedData_persian:… } }
    Returns a tuple: (extracted_data_english, extracted_data_persian)
    """
    if not resume_text.strip():
        logger.warning("Resume text is empty. Skipping LLM processing.")
        return None, None

    prompt = RESUME_PROCESSING_PROMPT_TEMPLATE.format(resume_text=resume_text)
    llm_response: LLMCallResult = await llm_async(
        prompt=prompt, # یا می‌توانید از پارامتر messages استفاده کنید
        system_message="You are an AI assistant that outputs JSON based on the user's resume text according to a specific schema.",
        llm_model_name=input_model, # یک متغیر جدید در settings برای نام مدل
        api_key=settings.OPENAI_API_KEY,
        # base_url=settings.OPENAI_BASE_URL, # یک متغیر جدید در settings برای base_url
        temperature=0.2, # برای دقت بیشتر در استخراج ساختاریافته
        max_tokens=5000, # ممکن است برای رزومه‌های طولانی و خروجی JSON بزرگ نیاز باشد
        response_format={"type": "json_object"}, # بسیار مهم برای دریافت JSON
        # سایر پارامترهای مورد نیاز ...
    )
    logger.debug(f"LLM response: {llm_response}")

    if not llm_response.success:
        logger.error(f"LLM call failed: {llm_response.message} - {llm_response.error_detail}")
        return None, None

    # ۱) نگاه کنیم آیا content رشته‌ای داریم:
    content_str: Optional[str] = None
    if isinstance(llm_response.content, str):
        content_str = llm_response.content
    # ۲) یا از full_response_data برشِ message.content را بگیریم:
    elif isinstance(llm_response.full_response_data, dict):
        choices = llm_response.full_response_data.get("choices", [])
        if choices and isinstance(choices[0], dict):
            msg = choices[0].get("message", {})
            content_str = msg.get("content")
    # اگر هیچ کدام پر نشده بود، خطا بدهیم:
    if not content_str:
        logger.error("No JSON content found in LLMCallResult.content or .full_response_data.")
        return None, None

    # ۳) حالا رشته‌ی محتوا را JSON بارگذاری کنیم:
    try:
        payload = json.loads(content_str)
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing LLM JSON content: {e}")
        logger.error(f"Raw content was:\n{content_str}")
        return None, None

    # ۴) از payload کلید parsedResult را برداریم:
    result_container = payload.get("parsedResult")
    if not isinstance(result_container, dict):
        logger.error("Key 'parsedResult' not found or not a dict in LLM response payload.")
        logger.error(f"Full payload: {payload}")
        return None, None

    # ۵) استخراج دو شیء مورد نظر:
    extracted_data_english = result_container.get("extractedData")
    extracted_data_persian = result_container.get("extractedData_persian")
    if not extracted_data_english:
        logger.error("Key 'extractedData' not found in parsedResult.")
        return None, None

    return extracted_data_english, extracted_data_persian