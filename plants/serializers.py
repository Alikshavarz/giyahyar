from rest_framework import serializers
from .models import Plant, PlantDiagnosis

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
