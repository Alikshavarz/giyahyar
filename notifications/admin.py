from django.contrib import admin
from .models import FCMDevice

@admin.register(FCMDevice)
class FCMDeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'registration_id', 'is_active', 'created_at')
    search_fields = ('user__username', 'registration_id')
    list_filter = ('is_active', 'created_at')
    ordering = ('-created_at',)