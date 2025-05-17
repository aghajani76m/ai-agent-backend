from app.services.file_service import FileService
from app.core.config import settings
from app.utils.pdf_parser import extract_text_from_pdf
from app.llm.calls.resume import process_resume_text
from app.core.dependencies import get_minio_client
from app.api.v1.schemas.resume import ExtractedResumeData, ProcessedResumeOutput # برای اعتبارسنجی
from elasticsearch import AsyncElasticsearch
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)

class ResumeProcessorService:    
    def __init__(self):
        self.minio_client = FileService() # در دنیای واقعی، اینها باید inject شوند (DI)
        # client Elasticsearch (async)
        es_kwargs = {"hosts": [{"host": settings.ES_HOST, "port": settings.ES_PORT, "scheme": "http"}]}
        if settings.ES_USER and settings.ES_PASS:
            es_kwargs["basic_auth"] = (settings.ES_USER,
                                       settings.ES_PASS)
        self.es = AsyncElasticsearch(**es_kwargs)
        # self.es_index = settings.ELASTICSEARCH_PROFILES_INDEX
    async def process_resume_from_minio(self, pdf_object_name_in_minio: str) -> ProcessedResumeOutput | None:
        """
        Processes a resume PDF from MinIO.
        pdf_object_name_in_minio: Full path to the PDF file in MinIO, e.g., "profiles/resume1.pdf"
        """
        logger.info(f"Starting processing for PDF: {pdf_object_name_in_minio}")

        # 1. Get PDF file from MinIO
        pdf_content = self.minio_client.get_file_content(pdf_object_name_in_minio)
        if not pdf_content:
            logger.error(f"Failed to retrieve PDF '{pdf_object_name_in_minio}' from MinIO.")
            return None

        # 2. Extract text from PDF
        logger.info("Extracting text from PDF...")
        resume_text = await extract_text_from_pdf(pdf_content)
        if not resume_text:
            logger.error(f"Failed to extract text from PDF '{pdf_object_name_in_minio}'.")
            return None
        logger.info(f"Extracted text (first 200 chars): {resume_text[:200]}...")

        # 3. Process text with LLM
        logger.info("Processing extracted text with LLM...")
        extracted_data_eng_dict, extracted_data_fa_dict = await process_resume_text(resume_text)

        if not extracted_data_eng_dict: # اگر خروجی انگلیسی موجود نباشد، احتمالا مشکلی پیش آمده
            logger.error(f"LLM failed to process resume text for '{pdf_object_name_in_minio}'.")
            return None
        
        # 4. Validate and structure the output using Pydantic models
        processed_output = ProcessedResumeOutput()
        try:            
            if extracted_data_eng_dict:
                processed_output.extractedData = ExtractedResumeData(**extracted_data_eng_dict)
            if extracted_data_fa_dict:
                # برای داده‌های فارسی هم می‌توانید از همان مدل ExtractedResumeData استفاده کنید
                # چون کلیدها انگلیسی هستند و فقط مقادیر رشته‌ای متفاوتند.
                processed_output.extractedData_persian = ExtractedResumeData(**extracted_data_fa_dict)
            logger.info(f"Successfully processed and validated data for '{pdf_object_name_in_minio}'.")
        except ValidationError as e:
            logger.error(f"Pydantic validation error for LLM output of '{pdf_object_name_in_minio}': {e}")
            logger.error(f"LLM English output: {extracted_data_eng_dict}")
            logger.error(f"LLM Persian output: {extracted_data_fa_dict}")
            # می‌توانید تصمیم بگیرید که آیا در صورت خطای اعتبارسنجی، None برگردانید
            # یا بخشی از داده‌ها را که معتبر هستند (اگر چنین منطقی پیاده‌سازی شود)
            return None # یا یک خروجی با خطای داخلی برگردانید

        # 5. (اختیاری) ذخیره JSON خروجی (مثلاً در Elasticsearch یا دیتابیس دیگر)
        # logger.info(f"Output for {pdf_object_name_in_minio}: {processed_output.model_dump_json(indent=2)}")
        # اینجا می‌توانید کد ذخیره‌سازی را اضافه کنید.
        # === 5. Store the JSON in Elasticsearch ===
        # از نام فایل (بدون پسوند) به عنوان ID سند استفاده می‌کنیم.
        # doc_id = pdf_object_name_in_minio.rsplit("/", 1)[-1].rsplit(".", 1)[0]
        # # دیکشنری نهایی خروجی
        # doc_body = processed_output.model_dump()
        # try:
        #     resp = await self.es.index(
        #         index=self.es_index,
        #         id=doc_id,
        #         document=doc_body,
        #         refresh="wait_for"  # تا سند قبل از بازگشت عملیات ایندکس شده باشد
        #     )
        #     logger.info(f"Indexed resume '{pdf_object_name_in_minio}' into ES index '{self.es_index}' (id={doc_id}), result: {resp['result']}")
        # except ElasticsearchException as es_e:
        #     logger.error(f"Error indexing resume '{pdf_object_name_in_minio}' into Elasticsearch: {es_e}")
        #     # در صورت تمایل می‌توانید باز هم processed_output را برگردانید یا None
        #     return processed_output

        return processed_output