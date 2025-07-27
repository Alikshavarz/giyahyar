from .models import Plant, PlantDiagnosis, WateringLog, WateringSchedule
from .serializers import PlantSerializer, PlantDiagnosisSerializer, WateringLogSerializer, WateringScheduleSerializer
from .services.ai_diagnosis_service import PlantDiagnosisService
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError as DRFValidationError
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

from django.conf import settings

# ======================================================
# لیست‌گیری و ایجاد گیاه جدید
class PlantListCreateView(generics.ListCreateAPIView):
    serializer_class = PlantSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Plant.objects.filter(user=self.request.user).order_by('-uploaded_at')

    def perform_create(self, serializer):
        serializer.save()


# ======================================================
class PlantRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PlantSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj = generics.get_object_or_404(
            Plant.objects.filter(user=self.request.user),
            pk=self.kwargs['pk']
        )
        return obj


# ======================================================
# آپلود تصویر گیاه و انجام تشخیص خودکار با هوش مصنوعی
class PlantDiagnosisCreateWithAIView(generics.CreateAPIView):
    serializer_class = PlantDiagnosisSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser) # برای پردازش آپلود فایل

    def perform_create(self, serializer):
        plant_id = self.kwargs.get('pk')
        if not plant_id:
            raise DRFValidationError({"plant": "Plant ID is required for diagnosis."})

        try:
            plant = Plant.objects.get(pk=plant_id, user=self.request.user)
        except Plant.DoesNotExist:
            raise NotFound("Plant not found or you don't have permission to diagnose it.")

        # بررسی محدودیت تعداد تشخیص‌ها (عکس‌ها)
        user_diagnoses_count = PlantDiagnosis.objects.filter(plant__user=self.request.user).count()
        if user_diagnoses_count >= 3 and not getattr(self.request.user, 'is_premium', False):
            raise PermissionDenied("Free diagnosis limit reached. Please upgrade to premium to upload more images.")

        diagnosis_instance = serializer.save(plant=plant)

        try:
            ai_service = PlantDiagnosisService(
                image_field=diagnosis_instance.image,
                api_key=settings.AI_API_KEY
            )
            ai_output = ai_service.diagnose()
            diagnosis_text = "No specific issue found."
            care_instructions_text = "General plant care advice."
            category_text = "other"
            confidence_score = 0.0

            if ai_output and 'suggestions' in ai_output and ai_output['suggestions']:
                best_suggestion = ai_output['suggestions'][0] # معمولا بهترین تشخیص اولین مورد است
                confidence_score = best_suggestion.get('probability', 0.0)

                if 'health_assessment' in ai_output and not ai_output['health_assessment'].get('is_healthy', True): # فرض می کنیم is_healthy میاد و اگر نیامد سالم در نظر می گیریم
                    problems = ai_output['health_assessment'].get('diseases', []) + ai_output['health_assessment'].get('pests', [])
                    if problems:
                        first_problem = problems[0]
                        diagnosis_text = f"مشکل احتمالی: {first_problem.get('name', 'ناشناخته')}"
                        care_instructions_text = best_suggestion.get('details', {}).get('wiki_description', 'دستورالعمل مراقبتی خاصی ارائه نشده است.')
                        category_text = "disease"
                    else:
                        diagnosis_text = "سلامت گیاه تایید نشد، اما مشکل خاصی شناسایی نشد."
                        category_text = "unhealthy_unknown"

                elif best_suggestion.get('name'):
                    diagnosis_text = f"شناسایی گیاه: {best_suggestion.get('name', 'ناشناخته')}"
                    care_instructions_text = best_suggestion.get('details', {}).get('wiki_description', '')
                    category_text = "identified"
            else:
                diagnosis_text = "تشخیص هوش مصنوعی امکان‌پذیر نبود. لطفاً تصویر واضح‌تری آپلود کنید."
                care_instructions_text = "لطفاً با کارشناس گیاه مشورت کنید."
                category_text = "other"


            diagnosis_instance.diagnosis = diagnosis_text
            diagnosis_instance.care_instructions = care_instructions_text
            diagnosis_instance.category = category_text
            diagnosis_instance.confidence = confidence_score
            diagnosis_instance.save()

        except Exception as e:
            print(f"Error during AI diagnosis for plant diagnosis {diagnosis_instance.id}: {e}")
            diagnosis_instance.diagnosis = f"AI diagnosis failed: {e}. Please ensure the image is clear and try again."
            diagnosis_instance.care_instructions = "Please upload a clearer image or consult a plant expert manually."
            diagnosis_instance.category = "other"
            diagnosis_instance.confidence = 0.0
            diagnosis_instance.save()
            raise DRFValidationError(f"AI diagnosis could not be completed: {e}")


# ======================================================
# لیست‌گیری تشخیص‌های گیاهان کاربر
class PlantDiagnosisListView(generics.ListAPIView):
    serializer_class = PlantDiagnosisSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PlantDiagnosis.objects.filter(plant__user=self.request.user).order_by('-created_at')


# ======================================================
# مشاهده، ویرایش یا حذف یک تشخیص خاص
class PlantDiagnosisRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PlantDiagnosisSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj = generics.get_object_or_404(
            PlantDiagnosis.objects.filter(plant__user=self.request.user),
            pk=self.kwargs['pk']
        )
        return obj


# ======================================================
# آبیاری جدید رو ثبت میکنه
class WateringLogCreateView(generics.CreateAPIView):
    serializer_class = WateringLogSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        plant_id = self.kwargs.get('pk')
        if not plant_id:
            raise DRFValidationError("Plant ID is required in the URL for recording watering.")

        try:
            plant = Plant.objects.get(pk=plant_id, user=self.request.user)
            note = serializer.validated_data.get('note', '')
            plant.mark_watered_today(note=note)

        except Plant.DoesNotExist:
            raise NotFound("The specified plant was not found or you do not have permission to water it.")
        except Exception as e:
            raise DRFValidationError(f"Error recording watering: {e}")


# ======================================================
# مناسب برای نمایش تاریخچه آبیاری یک گیاه خاص
class WateringLogListView(generics.ListAPIView):
    serializer_class = WateringLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        plant_id = self.kwargs.get('pk')
        if not plant_id:
            raise DRFValidationError("Plant ID is required in the URL to view watering history.")
        return WateringLog.objects.filter(plant__id=plant_id, plant__user=self.request.user).order_by('-watered_at')


# ======================================================
# لیست‌گیری و ایجاد زمان‌بندی آبیاری
class WateringScheduleListCreateView(generics.ListCreateAPIView):
    serializer_class = WateringScheduleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WateringSchedule.objects.filter(plant__user=self.request.user).order_by('plant__name')

    def perform_create(self, serializer):
        plant = serializer.validated_data['plant']
