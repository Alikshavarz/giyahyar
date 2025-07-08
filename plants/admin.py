from django.contrib import admin
from django.utils.html import format_html
from .models import Plant, PlantDiagnosis

class BaseAdmin(admin.ModelAdmin):
    @admin.display(description='Image Preview')
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 100px; height: auto;" />', obj.image.url)
        return ""

class PlantAdmin(BaseAdmin):
    list_display = (
        'name',
        'species',
        # 'user',
        'uploaded_at',
        'watering_frequency',
        'last_watered',
        'next_watering',
        'is_active',
        'image_preview',
    )
    # search_fields = ('name', 'species', 'user__username')
    list_filter = ('uploaded_at', 'is_active')
    list_editable = ('watering_frequency', 'is_active')
    readonly_fields = ('image_preview', 'uploaded_at', 'next_watering')

class PlantDiagnosisAdmin(BaseAdmin):
    list_display = (
        'plant',
        'category',
        'confidence',
        'created_at',
        'image_preview',
    )
    search_fields = ('diagnosis', 'plant__name')
    list_filter = ('category', 'created_at')
    readonly_fields = ('image_preview', 'created_at', 'diagnosis', 'care_instructions', 'confidence')

admin.site.register(Plant, PlantAdmin)
admin.site.register(PlantDiagnosis, PlantDiagnosisAdmin)
