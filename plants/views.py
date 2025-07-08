from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Plant, PlantDiagnosis
from .serializers import PlantSerializer, PlantDiagnosisSerializer
from giyahyar.utils import diagnose_plant  # فرض بر این است که این تابع تشخیص گیاه را انجام می‌دهد


# لیست‌گیری و ایجاد گیاه جدید
class PlantListCreateView(generics.ListCreateAPIView):
    queryset = Plant.objects.all()
    serializer_class = PlantSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # ذخیره گیاه جدید و اختصاص به کاربر
        plant = serializer.save(user=self.request.user)
        # محاسبه زمان آبیاری بعدی
        plant.update_next_watering()


# مشاهده، ویرایش یا حذف یک گیاه خاص
class PlantRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Plant.objects.all()
    serializer_class = PlantSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


# لیست‌گیری و ایجاد تشخیص جدید برای گیاه
class PlantDiagnosisListCreateView(generics.ListCreateAPIView):
    queryset = PlantDiagnosis.objects.all()
    serializer_class = PlantDiagnosisSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


# مشاهده، ویرایش یا حذف یک تشخیص خاص
class PlantDiagnosisRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PlantDiagnosis.objects.all()
    serializer_class = PlantDiagnosisSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


# آپلود تصویر گیاه و انجام تشخیص خودکار با هوش مصنوعی
class PlantImageUploadView(generics.CreateAPIView):
    queryset = Plant.objects.all()
    serializer_class = PlantSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # ذخیره گیاه جدید و اختصاص به کاربر
        plant = serializer.save(user=self.request.user)
        plant.update_next_watering()  # محاسبه زمان آبیاری بعدی

        # اجرای تشخیص با استفاده از مدل هوش مصنوعی
        diagnosis_info = diagnose_plant(plant.image)

        # اگر نتیجه‌ای از تشخیص دریافت شد، ذخیره شود
        if diagnosis_info:
            PlantDiagnosis.objects.create(
                plant=plant,
                diagnosis=diagnosis_info.get('diagnosis', ''),
                care_instructions=diagnosis_info.get('care_instructions', ''),
                category=diagnosis_info.get('category', 'other'),
                confidence=diagnosis_info.get('confidence', 0.0),
                image=diagnosis_info.get('image', plant.image)  # اگر تصویر جداگانه نبود، از تصویر گیاه استفاده شود
            )
