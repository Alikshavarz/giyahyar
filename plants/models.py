from django.db import models
from datetime import timedelta, date
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django.utils.translation import gettext_lazy as _


# 🌿 =========================================================

class Plant(models.Model):
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='plants/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # آبیاری
    watering_frequency = models.IntegerField(default=7, help_text="How often to water (in days)")
    last_watered = models.DateField(null=True, blank=True)
    next_watering = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.name

    def update_next_watering(self):
        """محاسبه زمان آبیاری بعدی بر اساس آخرین آبیاری و فاصله آبیاری"""
        if self.last_watered and self.watering_frequency:
            self.next_watering = self.last_watered + timedelta(days=self.watering_frequency)
            self.save()

    def mark_watered_today(self):
        """ثبت آبیاری امروز و به‌روزرسانی زمان بعدی"""
        self.last_watered = date.today()
        self.update_next_watering()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not hasattr(self, 'watering_schedule'):
            watering_schedule = WateringSchedule(plant=self, frequency=self.watering_frequency)
            watering_schedule.create_schedule()


# 🦠 =======================================================

class PlantDiagnosis(models.Model):
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name='diagnoses')
    image = models.ImageField(upload_to='diagnoses/')
    diagnosis = models.TextField()
    category = models.CharField(
        max_length=50,
        choices=[
            ('fungus', 'Fungus'),
            ('pest', 'Pest'),
            ('watering', 'Watering'),
            ('light', 'Light'),
            ('other', 'Other')
        ],
        default='other'
    )
    confidence = models.FloatField(default=0.0)
    care_instructions = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Diagnosis for {self.plant.name} - {self.created_at.strftime('%Y-%m-%d')}"


# 💧 ======================================================

class WateringLog(models.Model):
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name='watering_logs')
    watered_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True, help_text="توضیح اختیاری درباره آبیاری (مثلاً نوع آب یا شرایط خاص)")

    class Meta:
        ordering = ['-watered_at']

    def __str__(self):
        return f"{self.plant.name} watered on {self.watered_at.strftime('%Y-%m-%d %H:%M')}"

    def mark_watered_today(self):
        """ثبت آبیاری امروز و به‌روزرسانی زمان بعدی"""
        self.plant.last_watered = date.today()  # ثبت می‌کند که امروز گیاه آبیاری شده
        self.plant.update_next_watering()  # با توجه به watering_frequency، زمان آبیاری بعدی را محاسبه می‌کند
        self.plant.save()  # تغییرات را در دیتابیس ذخیره می‌کند
        WateringLog.objects.create(plant=self.plant)  # یک رکورد جدید در جدول WateringLog می‌سازد


# 🌊 ======================================================

class WateringSchedule(models.Model):
    plant = models.OneToOneField(Plant, on_delete=models.CASCADE, related_name='watering_schedule')
    frequency = models.IntegerField(help_text="آبیاری هر چند روز یک‌بار")  # مقدار روزها
    schedule = models.OneToOneField(PeriodicTask, on_delete=models.CASCADE, null=True, blank=True)

    def create_schedule(self):
        """ایجاد زمان‌بندی جدید برای آبیاری"""
        # ایجاد یا بازیابی یک زمان‌بندی جدید
        schedule, created = IntervalSchedule.objects.get_or_create(every=self.frequency, period=IntervalSchedule.DAYS)
        task = PeriodicTask.objects.create(
            interval=schedule,
            name=f"Water {self.plant.name}",
            task='tasks.water_plants'  # اطمینان حاصل کنید که مسیر به درستی مشخص شده است
        )
        self.schedule = task
        self.save()

    def __str__(self):
        return f"{self.plant.name} watering schedule every {self.frequency} days"