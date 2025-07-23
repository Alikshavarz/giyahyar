from django.contrib import admin
from .models import FCMDevice

@admin.register(FCMDevice)
class FCMDeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'registration_id', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('registration_id', 'user__username')
    readonly_fields = ('created_at',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')