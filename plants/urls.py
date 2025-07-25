from django.urls import path
from .views import (
    PlantListCreateView,
    PlantRetrieveUpdateDestroyView,
    PlantDiagnosisListCreateView,
    PlantDiagnosisRetrieveUpdateDestroyView,
    PlantImageUploadView,
    WateringLogCreateView,
    WateringLogListView,
    WateringScheduleListCreateView,
    WateringScheduleRetrieveUpdateDestroyView
)

urlpatterns = [
    # لیست‌گیری و ایجاد گیاه جدید
    path('plants/', PlantListCreateView.as_view(), name='plant-list-create'),

    # مشاهده، ویرایش یا حذف یک گیاه خاص
    path('plants/<int:pk>/', PlantRetrieveUpdateDestroyView.as_view(), name='plant-detail'),

    # آپلود تصویر گیاه و انجام تشخیص خودکار
    path('plants/upload/', PlantImageUploadView.as_view(), name='plant-image-upload'),


    # لیست‌گیری و ایجاد تشخیص برای گیاه
    path('diagnoses/', PlantDiagnosisListCreateView.as_view(), name='diagnosis-list-create'),

    # مشاهده، ویرایش یا حذف یک تشخیص خاص
    path('diagnoses/<int:pk>/', PlantDiagnosisRetrieveUpdateDestroyView.as_view(), name='diagnosis-detail'),

    # ثبت آبیاری جدید برای یک گیاه خاص
    path('plants/<int:pk>/water/', WateringLogCreateView.as_view(), name='plant-water'),

    # نمایش تاریخچه آبیاری برای یک گیاه خاص
    path('plants/<int:pk>/watering-history/', WateringLogListView.as_view(), name='watering-history'),


    # این ویو برای دریافت (GET) تمام زمان‌بندی‌ها و نیز ایجاد (POST) یک زمان‌بندی جدید استفاده می‌شود.
    path('watering-schedules/', WateringScheduleListCreateView.as_view(), name='watering-schedule-list-create'),

    # این ویو برای بازیابی (GET)، به‌روزرسانی (PUT/PATCH) و حذف (DELETE) یک زمان‌بندی خاص بر اساس pk (primary key) استفاده می‌شود.
    path('watering-schedules/<int:pk>/', WateringScheduleRetrieveUpdateDestroyView.as_view(), name='watering-schedule-detail'),
]