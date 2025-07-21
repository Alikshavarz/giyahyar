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
            return format_html('<img src="{}" style="width: 100px; height: auto; object-fit: contain;" />', obj.image.url)
        return ""

# ==========================
# 🌿 Inline: Watering Log
# ==========================
class WateringLogInline(admin.TabularInline):
    model = WateringLog
    extra = 0
    readonly_fields = ('watered_at',)
    ordering = ('-watered_at',)
    can_delete = False # ممکن است نخواهید لاگ‌های آبیاری را از اینجا حذف کنید

# ==========================
# 🌱 Inline: Plant Diagnosis
# ==========================
class PlantDiagnosisInline(admin.TabularInline):
    model = PlantDiagnosis
    extra = 0
    readonly_fields = (
        'created_at', 'diagnosis', 'category', 'confidence', 'care_instructions',
    )
    ordering = ('-created_at',)
    can_delete = True
    show_change_link = True

# ==========================
# 🌼 Admin: Plant
# ==========================
class PlantAdmin(BaseAdmin):
    list_display = (
        'name', 'user', 'species', 'uploaded_at', 'watering_frequency',
        'last_watered', 'next_watering', 'is_active', 'image_preview',
    )
    list_filter = ('uploaded_at', 'is_active', 'user') # فیلتر بر اساس کاربر
    search_fields = ['name', 'species', 'user__username'] # جستجو بر اساس نام کاربری
    list_editable = ('watering_frequency', 'is_active')
    readonly_fields = ('image_preview', 'uploaded_at', 'next_watering')
    inlines = [WateringLogInline, PlantDiagnosisInline]
    autocomplete_fields = ['user'] # برای سهولت انتخاب کاربر در صفحه ادمین

# ==========================
# 🦠 Admin: Plant Diagnosis
# ==========================
class PlantDiagnosisAdmin(BaseAdmin):
    list_display = (
        'plant', 'category', 'confidence', 'created_at', 'image_preview',
    )
    search_fields = ('diagnosis', 'plant__name', 'plant__user__username') # جستجو بر اساس نام گیاه و کاربر
    list_filter = ('category', 'created_at')
    readonly_fields = (
        'created_at', 'diagnosis', 'care_instructions', 'confidence', 'image_preview'
    )
    autocomplete_fields = ['plant']

# ==========================
# 💧 Admin: Watering Log
# ==========================
class WateringLogAdmin(admin.ModelAdmin):
    list_display = ('plant', 'watered_at', 'note')
    list_filter = ('watered_at', 'plant__user') # فیلتر بر اساس کاربر گیاه
    search_fields = ('plant__name', 'note', 'plant__user__username')
    ordering = ('-watered_at',)
    autocomplete_fields = ('plant',)

# ==========================
# 🌊 Admin: WateringSchedule
# ==========================
class WateringScheduleAdmin(admin.ModelAdmin):
    list_display = ('plant', 'frequency', 'schedule')
    search_fields = ('plant__name', 'plant__user__username')
    list_filter = ('frequency',)
    autocomplete_fields = ('plant',)

# ✅ Register Models
# ==========================
admin.site.register(Plant, PlantAdmin)
admin.site.register(PlantDiagnosis, PlantDiagnosisAdmin)
admin.site.register(WateringLog, WateringLogAdmin)
admin.site.register(WateringSchedule, WateringScheduleAdmin)