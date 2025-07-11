from .models import Plant, PlantDiagnosis, WateringLog
from .serializers import PlantSerializer, PlantDiagnosisSerializer, WateringLogSerializer
from giyahyar.utils import diagnose_plant  # فرض بر این است که این تابع تشخیص گیاه را انجام می‌دهد
from rest_framework.exceptions import NotFound
from rest_framework import serializers
from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.exceptions import PermissionDenied

# ======================================================
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

# ======================================================
# مشاهده، ویرایش یا حذف یک گیاه خاص

class PlantRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Plant.objects.all()
    serializer_class = PlantSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self):
        queryset = self.get_queryset()
        filter_kwargs = {'pk': self.kwargs['pk'], 'user': self.request.user}

        try:
            return queryset.get(**filter_kwargs)
        except Plant.DoesNotExist:
            raise NotFound("گیاه مورد نظر پیدا نشد.")

#  ======================================================
# لیست‌گیری و ایجاد تشخیص جدید برای گیاه

class PlantDiagnosisListCreateView(generics.ListCreateAPIView):
    queryset = PlantDiagnosis.objects.all()
    serializer_class = PlantDiagnosisSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

# ======================================================
# مشاهده، ویرایش یا حذف یک تشخیص خاص

class PlantDiagnosisRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PlantDiagnosis.objects.all()
    serializer_class = PlantDiagnosisSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

# ======================================================
# آپلود تصویر گیاه و انجام تشخیص خودکار با هوش مصنوعی

class PlantImageUploadView(generics.CreateAPIView):
    queryset = Plant.objects.all()
    serializer_class = PlantSerializer
    def perform_create(self, serializer):
        # ذخیره گیاه جدید و اختصاص به کاربر

        plant = serializer.save(user=self.request.user)
        plant.update_next_watering()  # محاسبه زمان آبیاری بعدی
        # اجرای تشخیص با استفاده از مدل هوش مصنوعی


        try:
            diagnosis_info = diagnose_plant(plant.image)
            if diagnosis_info:
                PlantDiagnosis.objects.create(
                    plant=plant,
                    diagnosis=diagnosis_info.get('diagnosis', ''),
                    care_instructions=diagnosis_info.get('care_instructions', ''),
                    category=diagnosis_info.get('category', 'other'),
                    confidence=diagnosis_info.get('confidence', 0.0),
                    image=diagnosis_info.get('image', plant.image)
                )
        except Exception as e:  # می‌توانید نوع خاصی از خطاها را مشخص کنید
            raise serializers.ValidationError(f"خطا در تشخیص گیاه: {str(e)}")

# ======================================================
#  آبیاری جدید رو ثبت میکنه

class WateringLogCreateView(generics.CreateAPIView):
    serializer_class = WateringLogSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        plant_id = self.kwargs['pk']
        try:
            plant = Plant.objects.get(pk=plant_id, user=self.request.user)
            plant.mark_watered_today()
            serializer.save(plant=plant)

        except Plant.DoesNotExist:
            raise PermissionDenied("شما اجازه ثبت آبیاری برای این گیاه را ندارید.")

        except Exception as e:
            raise serializers.ValidationError(f"خطا در ثبت آبیاری: {str(e)}")

# ======================================================
#  مناسب برای نمایش تاریخچه آبیاری یک گیاه خاص

class WateringLogListView(generics.ListAPIView):
    serializer_class = WateringLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        plant_id = self.kwargs['pk']
        return WateringLog.objects.filter(plant__id=plant_id, plant__user=self.request.user)

