from rest_framework import serializers
from .models import Plant, PlantDiagnosis, WateringLog, WateringSchedule
from django.db import transaction  # برای اطمینان از عملیات اتمیک


# =========================================================
class PlantSerializer(serializers.ModelSerializer):
    # این فیلد فقط برای نمایش است و مستقیماً ذخیره نمی‌شود
    user_plants_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Plant
        fields = (
            'id', 'name', 'species', 'description', 'image', 'uploaded_at',
            'watering_frequency', 'last_watered', 'next_watering', 'is_active',
            'user', 'user_plants_count'  # اضافه کردن user به فیلدها و user_plants_count
        )
        read_only_fields = ('uploaded_at', 'next_watering', 'user')  # کاربر را از context می‌گیریم

    def get_user_plants_count(self, obj):
        # این متد تعداد گیاهان کاربر فعلی را برمی‌گرداند
        # این برای نمایش اطلاعات به کاربر مفید است، اما برای اعتبارسنجی اصلی نیست
        if self.context and 'request' in self.context:
            user = self.context['request'].user
            return Plant.objects.filter(user=user).count()
        return None

    def create(self, validated_data):
        # اضافه کردن کاربر از context درخواست
        user = self.context['request'].user
        validated_data['user'] = user

        # اعتبارسنجی محدودیت آپلود
        if Plant.objects.filter(user=user).count() >= 3 and not getattr(user, 'is_premium', False):
            raise serializers.ValidationError("Free upload limit reached. Please upgrade to premium.")

        with transaction.atomic():  # اطمینان از اینکه عملیات اتمیک است
            plant = super().create(validated_data)
            plant.update_next_watering()  # محاسبهٔ خودکار زمان آبیاری بعدی

            # در اینجا WateringSchedule را ایجاد می‌کنیم
            # این کار اطمینان می‌دهد که زمان‌بندی برای هر گیاه جدید ایجاد شود
            WateringSchedule.objects.create(plant=plant, frequency=plant.watering_frequency)

        return plant

    def update(self, instance, validated_data):
        # در اینجا نیز می‌توانید اعتبارسنجی‌های مربوط به ویرایش را اضافه کنید
        return super().update(instance, validated_data)


# =========================================================
class PlantDiagnosisSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlantDiagnosis
        fields = (
            'id', 'plant', 'image', 'diagnosis', 'category', 'confidence',
            'care_instructions', 'created_at',
        )
        read_only_fields = ('diagnosis', 'category', 'confidence', 'care_instructions', 'created_at')


# =========================================================
class WateringLogSerializer(serializers.ModelSerializer):
    plant_name = serializers.CharField(source='plant.name', read_only=True)

    class Meta:
        model = WateringLog
        fields = (
            'id', 'plant', 'plant_name', 'watered_at', 'note',
        )
        read_only_fields = ('id', 'watered_at', 'plant_name')  # plant را برای ورودی لازم داریم

    def create(self, validated_data):
        # این متد فقط لاگ را ایجاد می‌کند. آبیاری در متد mark_watered_today گیاه انجام می‌شود.
        # در WateringLogCreateView، مستقیماً mark_watered_today فراخوانی می‌شود
        # بنابراین نیازی به این لاگیک در سریالایزر create نیست.
        # این سریالایزر می‌تواند برای نمایش (read-only) و یا در صورت نیاز برای ساخت مستقیم لاگ بدون تاثیر روی گیاه استفاده شود.
        return super().create(validated_data)


# =========================================================
class WateringScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = WateringSchedule
        fields = (
            'plant', 'frequency', 'schedule',
        )
        read_only_fields = ('schedule',)  # فقط خواندنی، زیرا این وظیفه به‌صورت خودکار ایجاد می‌شود

    def create(self, validated_data):
        # اگر زمان‌بندی برای این گیاه از قبل وجود دارد، خطا بده
        if WateringSchedule.objects.filter(plant=validated_data['plant']).exists():
            raise serializers.ValidationError({"plant": "A watering schedule already exists for this plant."})

        watering_schedule = WateringSchedule(**validated_data)
        watering_schedule.save()  # ابتدا مدل را ذخیره کن تا plant_id داشته باشد
        watering_schedule.create_schedule()  # سپس وظیفه زمان‌بندی را ایجاد کن
        return watering_schedule

    def update(self, instance, validated_data):
        instance.frequency = validated_data.get('frequency', instance.frequency)
        instance.save()  # تغییرات frequency را ذخیره کن
        instance.create_schedule()  # زمان‌بندی Celery Beat را با فرکانس جدید به‌روزرسانی کن
        return instance