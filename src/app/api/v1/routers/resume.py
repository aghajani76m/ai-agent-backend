from fastapi import APIRouter, HTTPException, Body, Query
from app.services.resume_minio_service import ResumeProcessorService
from app.api.v1.schemas.resume import ProcessedResumeOutput # مدل خروجی API
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resume", tags=["resume"])

resume_service = ResumeProcessorService() # برای سادگی؛ در عمل از Dependency Injection استفاده کنید
@router.post("/process-resume/", response_model=ProcessedResumeOutput)
async def process_resume_endpoint(
    # می‌توانید نام فایل را از query parameter یا body بگیرید
    # فرض می‌کنیم نام فایل در باکت profiles را به عنوان ورودی می‌گیریم
    pdf_filename: str = Query(
        ...,
        description="Name of the PDF file in the 'profiles' MinIO folder (e.g., 'my_cv.pdf')."
    ),
    pdf_file_id: str = Query(
        ...,
        description="if of the PDF file in the 'profiles' MinIO folder (e.g., '92ca585b-bf13-4c99-86ef-69b9c1783e75')."
    )
):
    """
    Processes a resume PDF file stored in MinIO.
    The PDF should be located in the 'profiles' folder within the configured MinIO bucket.
    """
    # نام کامل آبجکت در MinIO با احتساب پوشه 'profiles'
    minio_object_name = f"files/{pdf_file_id}_{pdf_filename}"
    
    logger.info(f"Received request to process resume: {minio_object_name}")
    try:
        result = await resume_service.process_resume_from_minio(minio_object_name)
        if result is None:
            # جزئیات بیشتر خطا باید در لاگ‌های سرویس ثبت شده باشد
            raise HTTPException(status_code=500, detail=f"Failed to process resume '{pdf_filename}'. Check server logs.")
        
        if not result.extractedData and not result.extractedData_persian:
             raise HTTPException(status_code=404, detail=f"Could not extract any data from resume '{pdf_filename}'. It might be empty or unprocessable.")

        return result
    except FileNotFoundError as e: # اگر باکت یا فایل در MinIO پیدا نشود
        logger.error(f"File not found error for {minio_object_name}: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception(f"An unexpected error occurred while processing {minio_object_name}: {e}")
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")

# می‌توانید یک اندپوینت دیگر برای آپلود فایل PDF به MinIO هم در نظر بگیرید،
# اما طبق درخواست فعلی، فرض بر این است که فایل از قبل در MinIO موجود است.```
