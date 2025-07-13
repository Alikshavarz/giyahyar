from django.contrib import admin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'username', 'phone_number', 'email', 'usage_count',
        'has_active_subscription', 'subscription_end'
    )
    search_fields = ('username', 'phone_number', 'email')
    list_filter = ('is_staff', 'is_superuser')
