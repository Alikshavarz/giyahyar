from .models import Plant, PlantDiagnosis, WateringLog, WateringSchedule
from .serializers import PlantSerializer, PlantDiagnosisSerializer, WateringLogSerializer, WateringScheduleSerializer
from utils import firebase_utils
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework import serializers
from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated


# ======================================================
# لیست‌گیری و ایجاد گیاه جدید
class PlantListCreateView(generics.ListCreateAPIView):
    serializer_class = PlantSerializer
    permission_classes = [IsAuthenticated]  # فقط کاربران احراز هویت شده می‌توانند ببینند یا ایجاد کنند

    def get_queryset(self):
        # فقط گیاهان متعلق به کاربر فعلی را نمایش می‌دهد
        return Plant.objects.filter(user=self.request.user).order_by('-uploaded_at')

    def perform_create(self, serializer):
        # این متد توسط PlantSerializer.create فراخوانی می‌شود
        # کاربر و اعتبارسنجی محدودیت آپلود در سریالایزر انجام می‌شود
        serializer.save()


# ======================================================
# مشاهده، ویرایش یا حذف یک گیاه خاص
class PlantRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Plant.objects.all()  # queryset عمومی
    serializer_class = PlantSerializer
    permission_classes = [IsAuthenticated]  # فقط کاربران احراز هویت شده

    def get_object(self):
        # فقط گیاهانی را بازیابی می‌کند که متعلق به کاربر فعلی باشند
        obj = generics.get_object_or_404(
            self.get_queryset().filter(user=self.request.user),
            pk=self.kwargs['pk']
        )
        return obj


# ======================================================
# آپلود تصویر گیاه و انجام تشخیص خودکار با هوش مصنوعی
class PlantImageUploadView(generics.CreateAPIView):
    queryset = Plant.objects.all()
    serializer_class = PlantSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        plant = serializer.save(user=self.request.user)

        try:
            diagnosis_info = diagnose_plant(plant.image.path)
            if diagnosis_info:
                PlantDiagnosis.objects.create(
                    plant=plant,
                    image=plant.image,  # از تصویر اصلی گیاه برای تشخیص استفاده می‌کنیم
                    diagnosis=diagnosis_info.get('diagnosis', 'No specific diagnosis found.'),
                    care_instructions=diagnosis_info.get('care_instructions',
                                                         'No specific care instructions provided.'),
                    category=diagnosis_info.get('category', 'other'),
                    confidence=diagnosis_info.get('confidence', 0.0),
                )
            else:
                PlantDiagnosis.objects.create(
                    plant=plant,
                    image=plant.image,
                    diagnosis="Could not determine a specific diagnosis for this plant. Please try again with a clearer image.",
                    care_instructions="Monitor your plant closely for any new symptoms.",
                    category="other",
                    confidence=0.0
                )
        except Exception as e:
              print(f"Error during plant diagnosis for plant {plant.id}: {e}")
              # raise serializers.ValidationError(f"Error in plant diagnosis: {str(e)}")


# ======================================================
# لیست‌گیری و ایجاد تشخیص جدید برای گیاه
class PlantDiagnosisListCreateView(generics.ListCreateAPIView):
    serializer_class = PlantDiagnosisSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PlantDiagnosis.objects.filter(plant__user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):

        serializer.save()


# ======================================================
# مشاهده، ویرایش یا حذف یک تشخیص خاص
class PlantDiagnosisRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PlantDiagnosis.objects.all()  # queryset عمومی
    serializer_class = PlantDiagnosisSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # فقط تشخیص‌هایی را بازیابی می‌کند که مربوط به گیاهان کاربر فعلی باشند
        obj = generics.get_object_or_404(
            self.get_queryset().filter(plant__user=self.request.user),
            pk=self.kwargs['pk']
        )
        return obj


# ======================================================
# آبیاری جدید رو ثبت میکنه
class WateringLogCreateView(generics.CreateAPIView):
    serializer_class = WateringLogSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        plant_id = self.kwargs.get('pk')  # pk گیاه از URL
        if not plant_id:
            raise serializers.ValidationError("Plant ID is required.")

        try:
            plant = Plant.objects.get(pk=plant_id, user=self.request.user)

            note = serializer.validated_data.get('note', '')
            plant.mark_watered_today(note=note)

        except Plant.DoesNotExist:
            raise NotFound("The specified plant was not found or you do not have permission to water it.")
        except Exception as e:
            raise serializers.ValidationError(f"Error recording watering: {str(e)}")


# ======================================================
# مناسب برای نمایش تاریخچه آبیاری یک گیاه خاص
class WateringLogListView(generics.ListAPIView):
    serializer_class = WateringLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        plant_id = self.kwargs.get('pk')
        if not plant_id:
            raise serializers.ValidationError("Plant ID is required.")
        # فقط لاگ‌های آبیاری مربوط به گیاهان کاربر فعلی را نمایش می‌دهد
        return WateringLog.objects.filter(plant__id=plant_id, plant__user=self.request.user).order_by('-watered_at')


# ======================================================
class WateringScheduleListCreateView(generics.ListCreateAPIView):
    serializer_class = WateringScheduleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WateringSchedule.objects.filter(plant__user=self.request.user).order_by('plant__name')

    def perform_create(self, serializer):
        plant = serializer.validated_data['plant']
        if plant.user != self.request.user:
            raise PermissionDenied("You do not have permission to create a watering schedule for this plant.")
        serializer.save()


class WateringScheduleRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = WateringSchedule.objects.all()
    serializer_class = WateringScheduleSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj = generics.get_object_or_404(
            self.get_queryset().filter(plant__user=self.request.user),
            pk=self.kwargs['pk']
        )
        return obj