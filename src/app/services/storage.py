# src/app/services/storage.py
from minio import Minio
from minio.error import S3Error
from app.core.config import settings

class StorageService:
    def __init__(self):
        self.client = Minio(
            endpoint=settings.MINIO_PUBLIC_ENDPOINT, # .replace("http://", "").replace("https://","")
            access_key=settings.MINIO_KEY,
            secret_key=settings.MINIO_SECRET,
            secure=settings.MINIO_SECURE,
            region=settings.MINIO_REGION
        )
        # ensure bucket exists
        if not self.client.bucket_exists(settings.FILES_BUCKET):
            self.client.make_bucket(settings.FILES_BUCKET)

    def upload_file(self, bucket: str, object_name: str, data: bytes, content_type: str):
        try:
            self.client.put_object(
                bucket_name=bucket,
                object_name=object_name,
                data=io.BytesIO(data),
                length=len(data),
                content_type=content_type
            )
        except S3Error as e:
            raise RuntimeError(f"Upload failed: {e}")

    def list_files(self, bucket: str, prefix: str):
        return list(self.client.list_objects(
            bucket_name=bucket,
            prefix=prefix,
            recursive=False
        ))

    def presign_url(self, bucket: str, object_name: str, expires: timedelta(seconds=36000)) -> str:
        return self.client.presigned_get_object(
            bucket_name=bucket,
            object_name=object_name,
            expires=expires
        )