from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # این مدل‌کانفیگ به Pydantic v2 می‌گوید از فایل .env بخواند
    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8"
    )

    # Server
    SERVER_HOST: str = Field("0.0.0.0", env="SERVER_HOST")
    SERVER_PORT: int = Field(8000, env="SERVER_PORT")

    # Elasticsearch
    ES_HOST: str = Field("elasticsearch", env="ES_HOST")
    ES_PORT: int = Field(9200, env="ES_PORT")
    ES_USER: str | None = Field(None, env="ES_USER")
    ES_PASS: str | None = Field(None, env="ES_PASS")

    # MinIO / S3
    # این برای کانتینر است
    MINIO_INTERNAL_ENDPOINT: str = "minio:9000"
    # این برای کاربر نهایی است (از بیرون داکر)
    MINIO_PUBLIC_ENDPOINT: str = Field("http://localhost:9000", env="MINIO_ENDPOINT")
    MINIO_KEY: str = Field(..., env="MINIO_KEY")
    MINIO_SECRET: str = Field(..., env="MINIO_SECRET")
    MINIO_BUCKET: str = Field("files", env="MINIO_BUCKET")
    MINIO_SECURE: bool = False   # True اگر https است
    FILES_BUCKET: str = "attachments"
    MINIO_REGION: str = "us-east-1"
    # OpenAI
    OPENAI_API_KEY: str = Field("aa-gH48KCQ475w3ffeBXXRweoiKcwZORnwxoYYBEjsWOp8nOY93", env="OPENAI_API_KEY")
    # TEMPERATURE: float = Field(0.7, env="TEMPERATURE")

settings = Settings()