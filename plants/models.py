from django.db import models
from datetime import timedelta, date
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django.utils.translation import gettext_lazy as _
from django.conf import settings  # برای ارجاع به مدل User


# =========================================================
class Plant(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # ارجاع به مدل User پیش‌فرض جنگو (یا مدل User کاستوم شما)
        on_delete=models.CASCADE,  # وقتی کاربر حذف شد، گیاهانش هم حذف شوند
        related_name='plants',  # برای دسترسی از User به گیاهانش (user.plants.all())
        verbose_name=_("User"),
        # **اینجا تغییر اصلی است:**
        # وقتی فیلد user را به مدل Plant اضافه می‌کنیم و از قبل در دیتابیس داده داریم،
        # Django نمی‌داند این فیلد جدید را برای داده‌های موجود چه مقداری بگذارد.
        # پس باید یک مقدار پیش‌فرض یک‌باره (one-off default) یا دائمی تعیین کنیم.
        # 'default=1' به این معنی است که تمام گیاهان موجود (هنگام اجرای migrate) به کاربری با ID=1 اختصاص داده شوند.
        # فرض بر این است که شما یک کاربر (معمولا ادمین) با ID=1 دارید.
        default=1
    )
    name = models.CharField(max_length=100, verbose_name=_("Plant Name"))
    species = models.CharField(max_length=100, blank=True, verbose_name=_("Species"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    image = models.ImageField(upload_to='plants/', verbose_name=_("Image"))
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Uploaded At"))

    # آبیاری
    watering_frequency = models.IntegerField(default=7, help_text=_("How often to water (in days)"),
                                             verbose_name=_("Watering Frequency"))
    last_watered = models.DateField(null=True, blank=True, verbose_name=_("Last Watered"))
    next_watering = models.DateField(null=True, blank=True, verbose_name=_("Next Watering"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = _("Plant")
        verbose_name_plural = _("Plants")

    def __str__(self):
        return self.name

    def update_next_watering(self):
        """محاسبه زمان آبیاری بعدی بر اساس آخرین آبیاری و فاصله آبیاری"""
        if self.last_watered and self.watering_frequency:
            self.next_watering = self.last_watered + timedelta(days=self.watering_frequency)
        else:
            self.next_watering = None  # اگر اطلاعات کافی نیست، زمان بعدی مشخص نیست
        self.save(update_fields=['next_watering'])  # فقط فیلد next_watering را ذخیره کن

    def mark_watered_today(self, note=""):
        """ثبت آبیاری امروز و به‌روزرسانی زمان بعدی و ثبت لاگ"""
        self.last_watered = date.today()
        self.update_next_watering()  # این متد خودش save می‌کند
        WateringLog.objects.create(plant=self, note=note)  # یک رکورد جدید در جدول WateringLog می‌سازد


# =======================================================
class PlantDiagnosis(models.Model):
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name='diagnoses', verbose_name=_("Plant"))
    image = models.ImageField(upload_to='diagnoses/', verbose_name=_("Diagnosis Image"))
    diagnosis = models.TextField(verbose_name=_("Diagnosis Result"))
    category = models.CharField(
        max_length=50,
        choices=[
            ('fungus', _('Fungus')),
            ('pest', _('Pest')),
            ('watering', _('Watering')),
            ('light', _('Light')),
            ('other', _('Other'))
        ],
        default='other',
        verbose_name=_("Category")
    )
    confidence = models.FloatField(default=0.0, verbose_name=_("Confidence"))
    care_instructions = models.TextField(verbose_name=_("Care Instructions"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Plant Diagnosis")
        verbose_name_plural = _("Plant Diagnoses")

    def __str__(self):
        return f"Diagnosis for {self.plant.name} - {self.created_at.strftime('%Y-%m-%d')}"


# ======================================================
class WateringLog(models.Model):
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name='watering_logs', verbose_name=_("Plant"))
    watered_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Watered At"))
    note = models.TextField(blank=True,
                            help_text=_("Optional note about watering (e.g., water type or special conditions)"),
                            verbose_name=_("Note"))

    class Meta:
        ordering = ['-watered_at']
        verbose_name = _("Watering Log")
        verbose_name_plural = _("Watering Logs")

    def __str__(self):
        return f"{self.plant.name} watered on {self.watered_at.strftime('%Y-%m-%d %H:%M')}"


# ======================================================
class WateringSchedule(models.Model):
    plant = models.OneToOneField(Plant, on_delete=models.CASCADE, related_name='watering_schedule',
                                 verbose_name=_("Plant"))
    frequency = models.IntegerField(help_text=_("Watering frequency in days"), verbose_name=_("Frequency"))
    schedule = models.OneToOneField(PeriodicTask, on_delete=models.SET_NULL, null=True, blank=True,
                                    verbose_name=_("Periodic Task Schedule"))  # Changed to SET_NULL for robustness

    def create_schedule(self):
        """ایجاد یا به‌روزرسانی زمان‌بندی Celery Beat برای آبیاری."""
        import json  # Import json inside the method

        # اگر از قبل زمان‌بندی وجود دارد، آن را حذف کن
        if self.schedule:
            self.schedule.delete()

        schedule, created = IntervalSchedule.objects.get_or_create(every=self.frequency, period=IntervalSchedule.DAYS)

        task = PeriodicTask.objects.create(
            interval=schedule,
            name=f"Water {self.plant.name} (Plant ID: {self.plant.id})",
            task='notifications.tasks.water_plants',
            kwargs=json.dumps({'plant_id': self.plant.id}),
            enabled=True,
            one_off=False,
            start_time=self.plant.next_watering or date.today()
        )
        self.schedule = task
        self.save()

    def __str__(self):
        return f"{self.plant.name} watering schedule every {self.frequency} days"

    # اضافه کردن متد delete برای حذف PeriodicTask هنگام حذف WateringSchedule
    def delete(self, *args, **kwargs):
        if self.schedule:
            self.schedule.delete()
        super().delete(*args, **kwargs)