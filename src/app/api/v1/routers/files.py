from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from minio import Minio
from app.services.file_service import FileService
from app.api.v1.schemas.file import FileOut, FileListOut
from app.core.dependencies import get_minio_client
from typing import List

router = APIRouter(prefix="/files", tags=["files"])


def get_file_service(minio_client: Minio = Depends(get_minio_client)):
    return FileService()


@router.post(
    "",
    response_model=FileOut,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a file",
    description="Upload a file to MinIO and index its metadata in Elasticsearch.",
    responses={
        201: {
            "description": "File successfully uploaded",
            "content": {
                "application/json": {
                    "example": {
                        "id": "file-abc123",
                        "filename": "invoice.pdf",
                        "content_type": "application/pdf",
                        "size": 102400,
                        "uploaded_at": "2025-05-07T12:00:00Z",
                        "url": "https://.../presigned-download-url"
                    }
                }
            }
        }
    }
)
async def upload_file(
    upload_file: UploadFile = File(...),
    svc: FileService = Depends(get_file_service)
):
    """
    - **upload_file**: the file to upload (PDF, image, text, etc.)
    """
    # UploadFile.file is a SpooledTemporaryFile
    result = svc.upload_file(
        file_stream=upload_file.file,
        filename=upload_file.filename,
        content_type=upload_file.content_type
    )
    return result


@router.get(
    "",
    response_model=FileListOut,
    summary="List all files",
    description="Retrieve metadata for all stored files.",
    responses={200: {"description": "List of files with metadata"}}
)
def list_files(
    svc: FileService = Depends(get_file_service)
):
    """
    - Returns a list of all files and their metadata.
    """
    files = svc.list_files()
    return FileListOut(files=files)


@router.get(
    "/{file_id}",
    response_model=FileOut,
    summary="Get file metadata & presigned URL",
    description="Fetch stored metadata and a presigned download URL for the file.",
    responses={
        200: {"description": "File metadata returned"},
        404: {"description": "File not found"}
    }
)
def get_file(
    file_id: str,
    svc: FileService = Depends(get_file_service)
):
    """
    - **file_id**: ID of the file to retrieve  
    """
    file = svc.get_file_by_id(file_id)
    if not file:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "File not found")
    return file


@router.delete(
    "/{file_id}/{filename}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a file",
    description="Remove the file object and its metadata.",
    responses={
        204: {"description": "File successfully deleted"},
        404: {"description": "File not found"}
    }
)
def delete_file(
    file_id: str,
    filename: str,
    svc: FileService = Depends(get_file_service)
):
    """
    - **file_id**: ID of the file to delete  
    - **filename**: original filename to confirm deletion  
    """
    ok = svc.delete_file(file_id, filename)
    if not ok:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "File not found")
    return