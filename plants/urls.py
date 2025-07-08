from django.urls import path
from .views import (
    PlantListCreateView,
    PlantRetrieveUpdateDestroyView,
    PlantDiagnosisListCreateView,
    PlantDiagnosisRetrieveUpdateDestroyView,
    PlantImageUploadView,
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
]
