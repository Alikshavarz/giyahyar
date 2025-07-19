from django.urls import path
from .views import FCMDeviceCreateUpdateView # View رو ایمپورت می‌کنیم

urlpatterns = [
    path('fcm-device/', FCMDeviceCreateUpdateView.as_view(), name='fcm_device_register_update'),
]