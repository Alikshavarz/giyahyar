from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import FCMDevice
from .serializers import FCMDeviceSerializer, FCMNotificationSerializer
from django.utils.translation import gettext_lazy as _
from .firebase_service import send_notification
import logging

logger = logging.getLogger(__name__)

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
            logger.info(f"New FCM token '{registration_id}' registered for user '{user.username}'.")
        else:
            logger.info(f"FCM token '{registration_id}' updated for user '{user.username}'.")

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

# --------------------------------------------

class FCMDeviceListView(generics.ListAPIView):
    serializer_class = FCMDeviceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FCMDevice.objects.filter(user=self.request.user, is_active=True)

# ------------------------------------------------

class FCMDeviceDeleteView(generics.DestroyAPIView):

    permission_classes = [permissions.IsAuthenticated]
    queryset = FCMDevice.objects.all()

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response({"detail": "شما اجازه حذف این توکن را ندارید."}, status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response({"detail": "توکن با موفقیت حذف شد."}, status=status.HTTP_204_NO_CONTENT)


# ------------------------------------

logger = logging.getLogger("notifications")

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
            logger.warning(f"⛔️ کاربر «{request.user.username}» هیچ توکن فعالی ندارد.")
            return Response(
                {"detail": _("توکن فعالی برای این کاربر یافت نشد.")},
                status=status.HTTP_404_NOT_FOUND
            )

        success, failure = 0, 0
        for device in devices:
            sent = send_notification(device.registration_id, title, body, data)
            if sent:
                success += 1
            else:
                failure += 1

        logger.info(f"📨 ارسال FCM برای کاربر «{request.user.username}»: موفق={success}, ناموفق={failure}")
        return Response({
            "sent": success,
            "failed": failure,
            "message": _("ارسال اعلان به پایان رسید.")
        }, status=status.HTTP_200_OK)




# در یکی از views.py یا یک فایل موقت برای تست
from django.http import HttpResponse
from firebase_admin import firestore

def test_firebase_firestore(request):
    try:
        db = firestore.client()
        doc_ref = db.collection('test_collection').document('test_document')
        doc_ref.set({
            'message': 'Hello from Django Firebase!',
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        return HttpResponse("Data written to Firestore successfully!")
    except Exception as e:
        return HttpResponse(f"Error writing to Firestore: {e}", status=500)