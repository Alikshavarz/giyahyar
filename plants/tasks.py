from celery import shared_task
from django.utils import timezone
from .models import Plant, WateringLog

@shared_task
def water_plants():
    today = timezone.now().date()
    # پیدا کردن گیاهانی که زمان آبیاری آن‌ها رسیده است
    plants = Plant.objects.filter(next_watering=today, is_active=True)

    for plant in plants:
        # آبیاری گیاه
        plant.mark_watered_today()  # به‌روزرسانی تاریخ آبیاری و ثبت آبیاری در تاریخچه
        WateringLog.objects.create(plant=plant)  # ثبت رکورد آبیاری
        print(f"{plant.name} has been watered.")