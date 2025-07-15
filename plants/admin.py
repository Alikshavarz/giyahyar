from django.contrib import admin
from django.utils.html import format_html
from .models import Plant, PlantDiagnosis, WateringLog, WateringSchedule

# ==========================
# 🔧 Base Admin with Image Preview
# ==========================
class BaseAdmin(admin.ModelAdmin):
    @admin.display(description='Image Preview')
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 100px; height: auto;" />', obj.image.url)
        return ""

# ==========================
# 🌿 Inline: Watering Log
# ==========================
class WateringLogInline(admin.TabularInline):
    model = WateringLog
    extra = 0
    readonly_fields = ('watered_at',)
    ordering = ('-watered_at',)

# ==========================
# 🌱 Inline: Plant Diagnosis
# ==========================
class PlantDiagnosisInline(admin.TabularInline):
    model = PlantDiagnosis
    extra = 0
    readonly_fields = (
        'created_at',
        'diagnosis',
        'category',
        'confidence',
        'care_instructions',

    )
    ordering = ('-created_at',)
    can_delete = True
    show_change_link = True

# ==========================
# 🌼 Admin: Plant
# ==========================
class PlantAdmin(BaseAdmin):
    list_display = (
        'name',
        'species',
        'uploaded_at',
        'watering_frequency',
        'last_watered',
        'next_watering',
        'is_active',
        'image_preview',
    )
    list_filter = ('uploaded_at', 'is_active')
    search_fields = ['name', 'species']
    list_editable = ('watering_frequency', 'is_active')
    readonly_fields = ('image_preview', 'uploaded_at', 'next_watering')
    inlines = [WateringLogInline, PlantDiagnosisInline]

# ==========================
# 🦠 Admin: Plant Diagnosis
# ==========================
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
    readonly_fields = (
        'created_at',
        'diagnosis',
        'care_instructions',
        'confidence',
    )

# ==========================
# 💧 Admin: Watering Log
# ==========================
class WateringLogAdmin(admin.ModelAdmin):
    list_display = ('plant', 'watered_at', 'note')
    list_filter = ('watered_at',)
    search_fields = ('plant__name', 'note')
    ordering = ('-watered_at',)
    autocomplete_fields = ('plant',)

# ==========================
# 💧 Admin: WateringSchedule

# =========================

class WateringScheduleAdmin(admin.ModelAdmin):
    list_display = ('plant', 'frequency', 'schedule')
    search_fields = ('plant__name',)
    # برای افزودن قابلیت فیلتر کردن
    list_filter = ('frequency',)



# ✅ Register Models
# ==========================
admin.site.register(Plant, PlantAdmin)
admin.site.register(PlantDiagnosis, PlantDiagnosisAdmin)
admin.site.register(WateringLog, WateringLogAdmin)
admin.site.register(WateringSchedule, WateringScheduleAdmin)
