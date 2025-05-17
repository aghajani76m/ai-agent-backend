# syntax=docker/dockerfile:1

FROM python:3.10.13

# جلوگیری از buffer شدن لاگ‌ها
ENV PYTHONUNBUFFERED=1

WORKDIR /ai_agent_backend/src/app

# 1) کپی و نصب dependencies
COPY src/app/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# 2) کپی کل سورس
COPY src/ .

# 3) باز کردن پورت (مطابق docker-compose.yml)
EXPOSE 8000

# 4) فرمان شروع اپ با Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]