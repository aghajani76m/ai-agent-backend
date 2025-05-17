import PyPDF2 # یا از کتابخانه دیگری مانند pdfminer.six استفاده کنید
import io
import logging

logger = logging.getLogger(__name__)

async def extract_text_from_pdf(pdf_content: bytes) -> str:
    """
    Extracts text from PDF content.
    """    
    text = ""
    try:
        pdf_file_object = io.BytesIO(pdf_content)        
        pdf_reader = PyPDF2.PdfReader(pdf_file_object)
        for page_num in range(len(pdf_reader.pages)):
            page_object = pdf_reader.pages[page_num]
            text += page_object.extract_text() + "\n" # اضافه کردن newline بین صفحات
        if not text.strip():
            logger.warning("Extracted text from PDF is empty. The PDF might be image-based or corrupted.")
        
        return text.strip()
    except PyPDF2.errors.PdfReadError as e:
        logger.error(f"Error reading PDF (PyPDF2): {e}. The PDF might be encrypted or corrupted.")
        return "" # یا یک خطا raise کنید
    except Exception as e:
        logger.error(f"An unexpected error occurred during PDF text extraction: {e}")
        return "" # یا یک خطا raise کنید