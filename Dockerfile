# استفاده از یک ایمیج پایه پایتون
FROM python:3.11-slim

# تنظیم متغیرهای محیطی
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# تنظیم دایرکتوری کاری
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# کپی کردن تمام فایل‌های پروژه به داخل کانتینر
COPY . /app/

# اجرای migrate و collectstatic
# RUN python manage.py migrate --no-input
# RUN python manage.py collectstatic --no-input

# مشخص کردن پورت مورد استفاده
EXPOSE 8000

# دستور نهایی برای اجرای پروژه
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]