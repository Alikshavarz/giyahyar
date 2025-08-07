from django.urls import path
from .views import FCMDeviceCreateUpdateView, FCMDeviceListView, FCMDeviceDeleteView
from . import views # یا از app.views import test_firebase_firestore

urlpatterns = [
    path('fcm-device/', FCMDeviceCreateUpdateView.as_view(), name='fcm_device_register_update'),
    path('device/list/', FCMDeviceListView.as_view(), name='fcm_device_list'),
    path('device/delete/<int:pk>/', FCMDeviceDeleteView.as_view(), name='fcm_device_delete'),
]