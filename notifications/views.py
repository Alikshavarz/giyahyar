from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import FCMDevice
from .serializers import FCMDeviceSerializer, FCMNotificationSerializer
from django.utils.translation import gettext_lazy as _
from .firebase_service import send_notification
import logging
from django.http import HttpResponse
from firebase_admin import firestore

logger = logging.getLogger(__name__)
notification_logger = logging.getLogger("notifications")


class FCMDeviceCreateUpdateView(generics.CreateAPIView):

    queryset = FCMDevice.objects.all()
    serializer_class = FCMDeviceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        registration_id = serializer.validated_data['registration_id']
        user = self.request.user


        fcm_device, created = FCMDevice.objects.update_or_create(
            registration_id=registration_id,
            defaults={'user': user, 'is_active': True}
        )
        serializer.instance = fcm_device

        if created:
            logger.info(f"✅ توکن جدید FCM '{registration_id}' برای کاربر '{user.username}' ثبت شد.")
        else:
            logger.info(f"🔄 توکن FCM '{registration_id}' برای کاربر '{user.username}' به روزرسانی شد (is_active=True).")

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                'message': _("FCM device token registered/updated successfully."),
                'token': serializer.instance.registration_id
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )


class FCMDeviceListView(generics.ListAPIView):

    serializer_class = FCMDeviceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FCMDevice.objects.filter(user=self.request.user, is_active=True)


class FCMDeviceDeleteView(generics.DestroyAPIView):

    permission_classes = [permissions.IsAuthenticated]
    queryset = FCMDevice.objects.all()

    def get_object(self):

        return super().get_object()

    def delete(self, request, *args, **kwargs):

        instance = self.get_object()
        if instance.user != request.user:
            notification_logger.warning(
                f"🚫 کاربر '{request.user.username}' تلاش کرد توکن FCM کاربر '{instance.user.username}' (ID: {instance.id}) را حذف کند.")
            return Response({"detail": _("شما اجازه حذف این توکن را ندارید.")}, status=status.HTTP_403_FORBIDDEN)

        token_id = instance.registration_id
        self.perform_destroy(instance)
        notification_logger.info(f"🗑️ توکن FCM '{token_id}' برای کاربر '{request.user.username}' با موفقیت حذف شد.")
        return Response({"detail": _("توکن با موفقیت حذف شد.")}, status=status.HTTP_204_NO_CONTENT)


class SendFCMNotificationView(generics.CreateAPIView):

    serializer_class = FCMNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        title = serializer.validated_data['title']
        body = serializer.validated_data['body']
        data = serializer.validated_data.get('data', {})

        devices = FCMDevice.objects.filter(user=request.user, is_active=True)

        if not devices.exists():
            notification_logger.warning(
                f"⛔️ کاربر «{request.user.username}» هیچ توکن فعالی برای ارسال نوتیفیکیشن ندارد.")
            return Response(
                {"detail": _("توکن فعالی برای این کاربر جهت ارسال اعلان یافت نشد.")},
                status=status.HTTP_404_NOT_FOUND
            )

        success_count, failure_count = 0, 0

        for device in devices:
            sent, error_msg = send_notification(device.registration_id, title, body, data)
            if sent:
                success_count += 1
            else:
                failure_count += 1
                notification_logger.error(
                    f"❌ ارسال FCM به توکن '{device.registration_id}' کاربر '{request.user.username}' ناموفق بود: {error_msg}"
                )
                # اگر خطا نشان‌دهنده یک توکن نامعتبر/منقضی شده است، آن را غیرفعال کنید.
                if error_msg and (
                        "InvalidRegistrationToken" in error_msg or "NotRegistered" in error_msg or "BadDeviceToken" in error_msg):
                    device.is_active = False
                    device.save()
                    notification_logger.warning(
                        f"⚠️ توکن FCM '{device.registration_id}' برای کاربر '{request.user.username}' غیرفعال شد (به دلیل نامعتبر بودن)."
                    )

        notification_logger.info(
            f"📨 ارسال FCM برای کاربر «{request.user.username}»: موفق={success_count}, ناموفق={failure_count}"
        )
        return Response({
            "sent": success_count,
            "failed": failure_count,
            "message": _("ارسال اعلان به پایان رسید.")
        }, status=status.HTTP_200_OK)




# -----------------------------------------
# views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny # برای تست موقت، اجازه هر کسی را می‌دهیم

# ایمپورت کردن توابع از firebase_service.py
from .firebase_service import send_notification
from decouple import config # برای خواندن FCM_TARGET_TOKEN از .env


class TestNotificationView(APIView):
    permission_classes = [AllowAny] # در محیط توسعه برای تست، اجازه دسترسی بدون احراز هویت را می‌دهیم

    def post(self, request):
        # این ویو برای ارسال نوتیفیکیشن با استفاده از توکن هدف ثابت طراحی شده است.
        # در یک سناریوی واقعی، شما توکن کاربر را از پایگاه داده یا درخواست دریافت می‌کنید.

        target_token = config('FCM_TARGET_TOKEN') # توکن دستگاه مقصد از فایل .env
        title = request.data.get('title', 'پیام تستی از جنگو')
        body = request.data.get('body', 'این یک نوتیفیکیشن تستی برای بررسی عملکرد است.')
        data = request.data.get('data', {}) # داده‌های اختیاری


        if not target_token:
            return Response(
                {"error": "FCM_TARGET_TOKEN در فایل .env تنظیم نشده است."},
                status=status.HTTP_400_BAD_REQUEST
            )

        success = send_notification(token=target_token, title=title, body=body, data=data)

        if success:
            return Response(
                {"message": "نوتیفیکیشن با موفقیت ارسال شد."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "ارسال نوتیفیکیشن با مشکل مواجه شد. لاگ‌های سرور را بررسی کنید."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )