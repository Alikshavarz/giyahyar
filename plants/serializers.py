from rest_framework import serializers
from .models import Plant, PlantDiagnosis, WateringLog, WateringSchedule
from django.db import transaction


# =========================================================
class PlantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plant
        fields = (
            'id', 'name', 'species', 'description', 'image', 'uploaded_at',
            'watering_frequency', 'last_watered', 'next_watering', 'is_active',
        )
        read_only_fields = ('uploaded_at', 'next_watering', 'user')


    # برای ایجاد پلنت جدید
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user


        with transaction.atomic():
            plant = super().create(validated_data)
            plant.update_next_watering()
            WateringSchedule.objects.create(plant=plant, frequency=plant.watering_frequency)

        return plant

    def update(self, instance, validated_data):
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
        read_only_fields = ('id', 'watered_at', 'plant_name')

    def create(self, validated_data):
        return super().create(validated_data)


# =========================================================
class WateringScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = WateringSchedule
        fields = (
            'plant', 'frequency', 'schedule',
        )
        read_only_fields = ('schedule',)

    def create(self, validated_data):
        if WateringSchedule.objects.filter(plant=validated_data['plant']).exists():
            raise serializers.ValidationError({"plant": "A watering schedule already exists for this plant."})

        with transaction.atomic():
            watering_schedule = WateringSchedule(**validated_data)
            watering_schedule.save()
            watering_schedule.create_schedule()
        return watering_schedule

    def update(self, instance, validated_data):
        instance.frequency = validated_data.get('frequency', instance.frequency)
        instance.save()
        instance.create_schedule()
        return instance