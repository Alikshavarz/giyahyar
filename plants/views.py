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
    queryset = Plant.objects.all()
    serializer_class = PlantSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Plant.objects.filter(user=self.request.user).order_by('-uploaded_at')

    def perform_create(self, serializer):
        serializer.save()


# ======================================================
class PlantRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Plant.objects.all()
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
    queryset = PlantDiagnosis.objects.all()
    serializer_class = PlantDiagnosisSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        plant_id = self.kwargs.get('pk')
        if not plant_id:
            raise DRFValidationError({"plant": "شناسه گیاه برای تشخیص لازم است"})

        try:
            plant = Plant.objects.get(pk=plant_id, user=self.request.user)
        except Plant.DoesNotExist:
            raise NotFound("گیاه پیدا نشد یا شما اجازه تشخیص آن را ندارید.")

        uploaded_images = self.request.FILES.getlist('images')
        if not uploaded_images:
            raise DRFValidationError({"images": "حداقل یک تصویر برای تشخیص لازم است."})


        diagnoses_count = PlantDiagnosis.objects.filter(plant__user=self.request.user).count()

        if diagnoses_count >= 3:
            raise DRFValidationError(
                {"subscription": "شما به سقف 3 تشخیص رایگان رسیده‌اید. برای تشخیص‌های بیشتر، لطفاً اشتراک تهیه کنید."})

        diagnosis_instance = serializer.save(plant=plant, image=uploaded_images[0])



        try:
            ai_service = PlantDiagnosisService(
                image_field=diagnosis_instance.image,
                api_key=settings.AI_API_KEY
            )
            ai_output = ai_service.diagnose()

            diagnosis_text = "مشکل خاصی پیدا نشد."
            care_instructions_text = "توصیه‌های کلی برای مراقبت از گیاه."
            category_text = "سایر"
            confidence_score = 0.0

            if ai_output and 'suggestions' in ai_output and ai_output['suggestions']:
                best_suggestion = ai_output['suggestions'][0]
                confidence_score = best_suggestion.get('probability', 0.0)

                if 'health_assessment' in ai_output and not ai_output['health_assessment'].get('is_healthy', True):
                    problems = ai_output['health_assessment'].get('diseases', []) + ai_output['health_assessment'].get(
                        'pests', [])
                    if problems:
                        first_problem = problems[0]
                        diagnosis_text = f"مشکل احتمالی: {first_problem.get('name', 'ناشناخته')}"
                        care_instructions_text = best_suggestion.get('details', {}).get('wiki_description',
                                                                                        'دستورالعمل مراقبتی خاصی ارائه نشده است.')
                        category_text = "بیماری"
                    else:
                        diagnosis_text = "سلامت گیاه تایید نشد، اما مشکل خاصی شناسایی نشد."
                        category_text = "ناسالم_ناشناخته"

                elif best_suggestion.get('plant_name'):
                    plant_details = best_suggestion.get('plant_details', {})
                    common_names = plant_details.get('common_names', [])
                    if common_names:
                        plant_name = common_names[0]
                    else:
                        plant_name = best_suggestion.get('plant_name', 'ناشناخته')

                    diagnosis_text = f"شناسایی گیاه: {plant_name}"
                    care_instructions_text = plant_details.get('wiki_description', {}).get('value', '')
                    category_text = "شناسایی_شده"
            else:
                diagnosis_text = "تشخیص هوش مصنوعی امکان‌پذیر نبود. لطفاً تصویر واضح‌تری آپلود کنید."
                care_instructions_text = "لطفاً با کارشناس گیاه مشورت کنید."
                category_text = "سایر"

            diagnosis_instance.diagnosis = diagnosis_text
            diagnosis_instance.care_instructions = care_instructions_text
            diagnosis_instance.category = category_text
            diagnosis_instance.confidence = confidence_score
            diagnosis_instance.save()

        except Exception as e:
            import traceback
            print("An error occurred during AI diagnosis:")
            traceback.print_exc()

            diagnosis_instance.diagnosis = f"تشخیص هوش مصنوعی ناموفق بود: {e}. لطفا از وضوح تصویر اطمینان حاصل کرده و دوباره امتحان کنید."
            diagnosis_instance.care_instructions = "لطفا تصویر واضح‌تری آپلود کنید یا به صورت دستی با یک کارشناس گیاه مشورت کنید."
            diagnosis_instance.category = "سایر"
            diagnosis_instance.confidence = 0.0
            diagnosis_instance.save()
            raise DRFValidationError(f"تشخیص هوش مصنوعی تکمیل نشد: {e}")


# ======================================================
# لیست‌گیری تشخیص‌های گیاهان کاربر
class PlantDiagnosisListView(generics.ListAPIView):
    queryset = PlantDiagnosis.objects.all()
    serializer_class = PlantDiagnosisSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PlantDiagnosis.objects.filter(plant__user=self.request.user).order_by('-created_at')


# ======================================================
# مشاهده، ویرایش یا حذف یک تشخیص خاص
class PlantDiagnosisRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PlantDiagnosis.objects.all()
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
    queryset = WateringLog.objects.all()
    serializer_class = WateringLogSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        plant_id = self.kwargs.get('pk')
        if not plant_id:
            raise DRFValidationError("شناسه گیاه برای ثبت آبیاری در url الزامی است.")

        try:
            plant = Plant.objects.get(pk=plant_id, user=self.request.user)
            note = serializer.validated_data.get('note', '')
            plant.mark_watered_today(note=note)

        except Plant.DoesNotExist:
            raise NotFound("گیاه مشخص شده پیدا نشد یا شما اجازه آبیاری آن را ندارید.")
        except Exception as e:
            raise DRFValidationError(f"خطا در ثبت آبیاری: {e}")


# ======================================================
# مناسب برای نمایش تاریخچه آبیاری یک گیاه خاص
class WateringLogListView(generics.ListAPIView):
    serializer_class = WateringLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return WateringLog.objects.none()

        plant_id = self.kwargs.get('pk')
        if not plant_id:
            raise DRFValidationError("شناسه گیاه (Plant ID) برای مشاهده تاریخچه آبیاری در URL الزامی است.")

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










