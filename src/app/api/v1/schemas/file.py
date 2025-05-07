from datetime import datetime
from pydantic import BaseModel, Field

class FileOut(BaseModel):
    id: str = Field(..., example="generated-file-id")
    filename: str = Field(..., example="invoice.pdf")
    content_type: str = Field(..., example="application/pdf")
    size: int = Field(..., example=102400)
    uploaded_at: datetime
    url: str = Field(..., example="presigned-download-url")

class FileListOut(BaseModel):
    files: list[FileOut]