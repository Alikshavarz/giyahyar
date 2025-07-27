from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username', 'first_name', 'last_name', 'phone_number',
        'is_phone_verified', 'feature_usage_count', 'is_active'
    )
    readonly_fields = ('feature_usage_count', 'sms_code', 'sms_code_expiry')
