FROM python:3.11-slim

WORKDIR /app

# ضبط متغيرات البيئة للمنطقة الزمنية
ENV TZ=Europe/Istanbul
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# تثبيت تبعيات النظام بما في ذلك tzdata لضبط الوقت
RUN apt-get update && apt-get install -y \
    postgresql-client \
    tzdata \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
    && rm -rf /var/lib/apt/lists/*

# نسخ ملف المتطلبات وتثبيت مكتبات بايثون
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ ملفات المشروع
COPY . .

# فتح المنفذ 8000
EXPOSE 8000

# الأمر الافتراضي لتشغيل المشروع
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]