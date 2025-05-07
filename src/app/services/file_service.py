import uuid
from datetime import datetime, timedelta
from typing import List, Optional
from io import BytesIO
from urllib.parse import urlsplit, urlunsplit

from minio import Minio
from minio.error import S3Error

from app.core.config import settings
from app.api.v1.schemas.file import FileOut

class FileService:
    def __init__(self, minio_client: Minio):
        self.client = minio_client
        self.bucket = settings.FILES_BUCKET
        # این برای ساختن presigned URL برای کلاینت‌های بیرونی
        # parse کردن public endpoint از تنظیمات
        url = urlsplit(settings.MINIO_PUBLIC_ENDPOINT)
        public_endpoint = url.netloc             # e.g. "localhost:9000"
        public_secure   = (url.scheme == "https") 

        self.presign_client = Minio(
            endpoint=public_endpoint,
            access_key=settings.MINIO_KEY,
            secret_key=settings.MINIO_SECRET,
            secure=public_secure,
            region=settings.MINIO_REGION
        )

    def upload_file(self, file_stream, filename: str, content_type: str) -> FileOut:
        # 1) اول کل داده‌ها را در حافظه بخوانیم
        data = file_stream.read()
        size = len(data)
        # 2) بوبفری بسازیم تا بتوانیم آن را دوباره بفرستیم
        byte_stream = BytesIO(data)

        file_id = str(uuid.uuid4())
        object_name = f"{file_id}/{filename}"

        # 3) آپلود با طول مشخص
        self.client.put_object(
            bucket_name=self.bucket,
            object_name=object_name,
            data=byte_stream,
            length=size,              # این‌جا طول را می‌دهیم
            content_type=content_type
        )

        # 4) گرفتن stat برای متا
        stat = self.client.stat_object(self.bucket, object_name)
        # internal_url = self.client.presigned_get_object(
        #     self.bucket, object_name, expires=timedelta(seconds=36000)
        # )

        # # حالا آن را به PUBLIC_ENDPOINT تبدیل می‌کنیم:
        # parts = urlsplit(internal_url)
        # # parts = (scheme, netloc, path, query, fragment)
        # public_netloc = settings.MINIO_PUBLIC_ENDPOINT.replace("http://", "").replace("https://", "")
        # public_scheme = settings.MINIO_PUBLIC_ENDPOINT.split("://")[0]
        # public_url = urlunsplit((public_scheme, public_netloc, parts.path, parts.query, parts.fragment))
        uploaded_at = (
            datetime.fromtimestamp(stat.last_modified.timestamp())
            if stat.last_modified else datetime.utcnow().timestamp()  # یا مقدار پیش‌فرض دلخواه
        )

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

    def get_presigned_url(self, file_id: str, filename: str, expires: datetime = timedelta(seconds=36000)) -> str:
        object_name = f"{file_id}/{filename}"
        return self.presign_client.presigned_get_object(
            bucket_name=self.bucket,
            object_name=object_name,
            expires=expires
        )
    def delete_file(self, file_id: str, filename: str) -> bool:
        object_name = f"{file_id}/{filename}"
        try:
            self.client.remove_object(self.bucket, object_name)
            return True
        except S3Error:
            return False

    def list_files(self) -> List[FileOut]:
        out = []
        # لیست objectها را پیمایش می‌کنیم
        for obj in self.client.list_objects(self.bucket, recursive=True):
            # obj.object_name = "{file_id}/{filename}"
            file_id, filename = obj.object_name.split("/", 1)
            url = self.presign_client.presigned_get_object(self.bucket, obj.object_name, expires=timedelta(seconds=36000))
            uploaded_at = (
                datetime.fromtimestamp(obj.last_modified.timestamp())
                if obj.last_modified else datetime.utcnow().timestamp()  # یا مقدار پیش‌فرض دلخواه
            )
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
        for obj in self.client.list_objects(self.bucket, prefix=f"{file_id}/", recursive=True):
            try:
                file_id_extracted, filename = obj.object_name.split("/", 1)
                if file_id_extracted != file_id:
                    continue

                url = self.presign_client.presigned_get_object(
                    self.bucket, obj.object_name, expires=timedelta(seconds=3600)
                )
                uploaded_at = (
                    datetime.fromtimestamp(obj.last_modified.timestamp())
                    if obj.last_modified else datetime.utcnow()
                )

                return FileOut(
                    id=file_id,
                    filename=filename,
                    content_type=obj.content_type or "application/octet-stream",
                    size=obj.size,
                    uploaded_at=uploaded_at,
                    url=url
                )
            except Exception:
                continue
        return None
