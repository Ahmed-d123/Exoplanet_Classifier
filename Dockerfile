# استخدم Python stable image
FROM python:3.10-slim

# حل مشكلة libgomp
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# انسخ الملفات
COPY requirements.txt .

# نزّل المكتبات
RUN pip install --no-cache-dir -r requirements.txt

# انسخ باقي الملفات
COPY . .

# شغّل السيرفر
CMD ["python","-m","uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
