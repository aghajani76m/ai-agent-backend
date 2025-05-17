import uuid
from datetime import datetime, timedelta
from typing import List, Optional
from io import BytesIO
from urllib.parse import urlsplit, urlunsplit

from minio import Minio
from minio.error import S3Error

from app.core.config import settings
from app.api.v1.schemas.file import FileOut
import logging

logger = logging.getLogger(__name__)

class FileService:
    def __init__(self):
        # کلاینت داخلی MinIO
        self.client = Minio(
            endpoint=settings.MINIO_INTERNAL_ENDPOINT,
            access_key=settings.MINIO_KEY,
            secret_key=settings.MINIO_SECRET,
            secure=settings.MINIO_SECURE,
            region=settings.MINIO_REGION
        )
        # زیرپوشۀ ثابت برای آپلود
        self.upload_prefix = settings.MINIO_BUCKET   # معمولاً "files"
        self.bucket = settings.FILES_BUCKET          # مثلاً "attachments"

        # کلاینت presign برای URL بیرونی
        parts = urlsplit(settings.MINIO_PUBLIC_ENDPOINT)
        self.presign_client = Minio(
            endpoint=parts.netloc,
            access_key=settings.MINIO_KEY,
            secret_key=settings.MINIO_SECRET,
            secure=(parts.scheme == "https"),
            region=settings.MINIO_REGION
        )

    def upload_file(self, file_stream, filename: str, content_type: str) -> FileOut:
        try:
            data = file_stream.read()
            size = len(data)
            byte_stream = BytesIO(data)

            file_id = str(uuid.uuid4())
            # الگوی جدید object_name:
            object_name = f"{self.upload_prefix}/{file_id}_{filename}"

            self.client.put_object(
                bucket_name=self.bucket,
                object_name=object_name,
                data=byte_stream,
                length=size,
                content_type=content_type
            )

            stat = self.client.stat_object(self.bucket, object_name)
            uploaded_at = stat.last_modified or datetime.utcnow()

            url = self.presign_client.presigned_get_object(
                bucket_name=self.bucket,
                object_name=object_name,
                expires=timedelta(seconds=36000)
            )
            return FileOut(
                id=file_id,
                filename=filename,
                content_type=content_type,
                size=stat.size,
                uploaded_at=uploaded_at,
                url=url
            )

        except S3Error as e:
            logger.error(f"MinIO S3Error during upload: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Unexpected error in upload_file: {e}", exc_info=True)
            raise

    def get_presigned_url(self, file_id: str, filename: str,
                          expires: timedelta = timedelta(seconds=36000)
    ) -> str:
        # مطابق الگوی جدید:
        object_name = f"{self.upload_prefix}/{file_id}_{filename}"
        return self.presign_client.presigned_get_object(
            bucket_name=self.bucket,
            object_name=object_name,
            expires=expires
        )

    def delete_file(self, file_id: str, filename: str) -> bool:
        object_name = f"{self.upload_prefix}/{file_id}_{filename}"
        try:
            self.client.remove_object(self.bucket, object_name)
            return True
        except S3Error:
            return False

    def list_files(self) -> List[FileOut]:
        out: List[FileOut] = []
        for obj in self.client.list_objects(self.bucket, recursive=True):
            key = obj.object_name
            # فیلتر کردن غیر مرتبط‌ها
            if not key.startswith(f"{self.upload_prefix}/"):
                continue
            # حذف پیش‌وند و استخراج file_id و filename
            rest = key[len(self.upload_prefix) + 1:]      # "uuid_filename.ext"
            file_id, filename = rest.split("_", 1)

            url = self.presign_client.presigned_get_object(
                bucket_name=self.bucket,
                object_name=key,
                expires=timedelta(seconds=36000)
            )
            uploaded_at = obj.last_modified or datetime.utcnow()

            out.append(FileOut(
                id=file_id,
                filename=filename,
                content_type=obj.content_type or "application/octet-stream",
                size=obj.size,
                uploaded_at=uploaded_at,
                url=url
            ))
        return out

    def get_file_by_id(self, file_id: str) -> Optional[FileOut]:
        prefix = f"{self.upload_prefix}/{file_id}_"
        for obj in self.client.list_objects(self.bucket, prefix=prefix, recursive=True):
            key = obj.object_name
            # rest = "{file_id}_{filename}"
            rest = key[len(prefix):]
            filename = rest

            url = self.presign_client.presigned_get_object(
                bucket_name=self.bucket,
                object_name=key,
                expires=timedelta(seconds=36000)
            )
            uploaded_at = obj.last_modified or datetime.utcnow()

            return FileOut(
                id=file_id,
                filename=filename,
                content_type=obj.content_type or "application/octet-stream",
                size=obj.size,
                uploaded_at=uploaded_at,
                url=url
            )
        return None

    def get_file_content(self, object_name: str) -> bytes | None:
        response = None
        try:
            response = self.client.get_object(
                bucket_name=self.bucket,
                object_name=object_name
            )
            return response.read()
        except S3Error as e:
            logger.error(f"Error getting file {object_name} from MinIO: {e}")
            if getattr(e, "code", None) == "NoSuchKey":
                logger.warning(f"File {object_name} not found in bucket {self.bucket}.")
                return None
            return None
        finally:
            if response:
                try:
                    response.close()
                    response.release_conn()
                except Exception:
                    pass


################# this function returns url of file and then download it with requests
# from datetime import timedelta
# from minio.error import S3Error
# import requests
# import logging

# logger = logging.getLogger(__name__)

# class FileService:
#     # فرض می‌کنیم self.presign_client = Minio(...) قبلاً تنظیم شده
#     def get_file_content(self, object_name: str) -> bytes | None:
#         """
#         Retrieves a file from MinIO using a presigned URL and requests.
#         """
#         try:
#             # ۱. URL پیش‌امضا شده بگیرید
#             url: str = self.presign_client.presigned_get_object(
#                 bucket_name=self.bucket,
#                 object_name=object_name,
#                 expires=timedelta(seconds=36000)
#             )
#             # ۲. با requests دانلود کنید
#             resp = requests.get(url, timeout=60)
#             resp.raise_for_status()  # اگر کد وضعیت != 200 بود خطا پرتاب کند
#             return resp.content

#         except S3Error as e:
#             logger.error(f"Error creating presigned URL for {object_name}: {e}")
#             if e.code == "NoSuchKey":
#                 logger.warning(f"File {object_name} not found in bucket {self.bucket}.")
#                 return None
#             raise

#         except requests.HTTPError as e:
#             logger.error(f"HTTP error downloading {object_name} from presigned URL: {e}")
#             return None

#         except requests.RequestException as e:
#             logger.error(f"Error downloading {object_name} from presigned URL: {e}")
#             return None

#         # no finally needed since we're not holding a stream-like response