from rest_framework import serializers
from .models import Plant, PlantDiagnosis, WateringLog, WateringSchedule

class PlantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plant
        fields = (
            'id',
            'name',
            'species',
            'description',
            'image',
            'uploaded_at',
            'watering_frequency',
            'last_watered',
            'next_watering',
            'is_active',
        )
        read_only_fields = ('uploaded_at', 'next_watering')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        plant = super().create(validated_data)
        plant.update_next_watering() # محاسبهٔ خودکار زمان آبیاری بعدی
        return plant

    def validate(self, attrs):
        user = self.context['request'].user
        if Plant.objects.filter(user=user).count() >= 3 and not getattr(user, 'is_premium', False):
            raise serializers.ValidationError("Free upload limit reached. Please upgrade to premium.")
        return attrs


class PlantDiagnosisSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlantDiagnosis
        fields = (
            'id',
            'plant',
            'image',
            'diagnosis',
            'category',
            'confidence',
            'care_instructions',
            'created_at',
        )
        read_only_fields = ('diagnosis', 'category', 'confidence', 'care_instructions', 'created_at')




class WateringLogSerializer(serializers.ModelSerializer):
    plant_name = serializers.CharField(source='plant.name', read_only=True)

    class Meta:
        model = WateringLog
        fields = (
            'id',
            'plant',
            'plant_name',
            'watered_at',
            'note',
        )
        read_only_fields = ('id', 'watered_at', 'plant_name')

    def create(self, validated_data):
        # ایجاد لاگ جدید
        watering_log = super().create(validated_data)
        watering_log.mark_watered_today()  # ثبت آبیاری در گیاه
        return watering_log


class WateringScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = WateringSchedule
        fields = (
            'plant',
            'frequency',
            'schedule',
        )

        read_only_fields = ('schedule',)  # فقط خواندنی، زیرا این وظیفه به‌صورت خودکار ایجاد می‌شود

    def create(self, validated_data):
        # ایجاد آب‌دادن جدید
        watering_schedule = WateringSchedule(**validated_data)
        watering_schedule.create_schedule()  # ایجاد وظیفه زمان‌بندی برای آب‌دادن
        watering_schedule.save()  # ذخیره مدل
        return watering_schedule

    def update(self, instance, validated_data):
        # بروزرسانی فرکانس اگر تغییر کند
        frequency = validated_data.get('frequency', instance.frequency)
        instance.frequency = frequency

        if instance.frequency != frequency:
            instance.create_schedule()  # در صورت تغییر فرکانس، وظیفه زمان‌بندی را به‌روزرسانی کنید
        instance.save()  # ذخیره تغییرات
        return instance
