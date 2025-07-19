from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import FCMDevice
from .serializers import FCMDeviceSerializer
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class FCMDeviceCreateUpdateView(generics.CreateAPIView):
    """
    View برای ثبت یا به‌روزرسانی توکن FCM دستگاه کاربر.
    اگر توکن قبلاً برای کاربر وجود داشته باشد، به‌روزرسانی می‌شود.
    اگر وجود نداشته باشد، یک رکورد جدید ایجاد می‌شود.
    """
    queryset = FCMDevice.objects.all()
    serializer_class = FCMDeviceSerializer
    permission_classes = [permissions.IsAuthenticated] # فقط کاربران احراز هویت شده می‌توانند توکن ثبت کنند

    def perform_create(self, serializer):
        """
        این متد قبل از ذخیره کردن شیء فراخوانی می‌شود.
        ما از این متد برای اختصاص کاربر فعلی به توکن و همچنین
        برای به‌روزرسانی توکن در صورت وجود قبلی استفاده می‌کنیم.
        """
        registration_id = serializer.validated_data['registration_id']
        user = self.request.user # کاربر فعلی که درخواست را ارسال کرده

        # تلاش برای پیدا کردن یا ایجاد/به‌روزرسانی توکن برای کاربر فعلی
        # اگر توکن قبلاً برای این کاربر وجود داشته باشد، آن را به‌روزرسانی می‌کند.
        # اگر توکن برای کاربر دیگری وجود داشته باشد، این باعث ایجاد یک رکورد جدید می‌شود.
        # اما چون registration_id unique است، اگر توکن دقیقاً همین باشد،
        # Django یک خطا می‌دهد. پس منطق باید کمی متفاوت باشد تا
        # اگر توکن برای کاربر فعلی وجود دارد، آن را آپدیت کند.

        # بهترین راه برای این سناریو این است که ابتدا بررسی کنیم آیا
        # توکنی با این registration_id وجود دارد یا نه.
        # اگر وجود دارد، آن را به کاربر فعلی اختصاص دهیم (اگر کاربرش فرق دارد)
        # یا اگر کاربرش همین است، کاری نکنیم.
        # اگر وجود ندارد، یک رکورد جدید بسازیم.

        try:
            # سعی می‌کنیم دستگاهی با این registration_id پیدا کنیم
            fcm_device = FCMDevice.objects.get(registration_id=registration_id)
            # اگر پیدا شد و کاربرش متفاوت بود، آن را به کاربر فعلی اختصاص می‌دهیم
            if fcm_device.user != user:
                fcm_device.user = user
                fcm_device.save()
            # اگر پیدا شد و کاربرش همین بود، یعنی توکن قبلاً ثبت شده و نیازی به تغییر نیست.
            serializer.instance = fcm_device # برای اینکه پاسخ View درست باشه
            print(f"FCM token '{registration_id}' updated/already exists for user '{user.username}'.")
        except FCMDevice.DoesNotExist:
            # اگر توکنی با این registration_id وجود نداشت، یک رکورد جدید ایجاد می‌کنیم
            serializer.save(user=user)
            print(f"New FCM token '{registration_id}' registered for user '{user.username}'.")

    def create(self, request, *args, **kwargs):
        """
        متد create رو override می‌کنیم تا پیام‌های موفقیت‌آمیز و خطا رو بهتر مدیریت کنیم.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {'message': _("FCM device token registered/updated successfully."), 'token': serializer.instance.registration_id},
            status=status.HTTP_201_CREATED,
            headers=headers
        )
