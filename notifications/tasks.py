from celery import shared_task
from plants.models import Plant
from .models import FCMDevice
import logging
from .firebase_service import send_notification

logger = logging.getLogger(__name__)


@shared_task(bind=True, default_retry_delay=300, max_retries=5)
def water_plants(self, plant_id):
    try:
        plant = Plant.objects.get(id=plant_id)
        logger.info(
            f"آماده‌سازی برای ارسال اعلان آبیاری برای گیاه: {plant.name} (شناسه: {plant.id}) برای کاربر: {plant.user.username}"
        )

        try:
            fcm_devices = FCMDevice.objects.filter(user=plant.user, is_active=True)

            if not fcm_devices.exists():
                logger.warning(
                    f"هیچ توکن FCM فعالی برای کاربر {plant.user.username} (گیاه: {plant.name}) یافت نشد. اعلان نادیده گرفته شد."
                )
                return

            for fcm_device in fcm_devices:
                token = fcm_device.registration_id

                if not token:
                    logger.warning(
                        f"توکن ثبت FCM برای یک دستگاه کاربر {plant.user.username} (گیاه: {plant.name}) خالی است. این دستگاه نادیده گرفته شد."
                    )
                    continue

                # پیام‌هایی که به کاربر نمایش داده می‌شوند
                title = f"زمان آبیاری {plant.name}!"
                body = f"گیاه زیبای {plant.name} نیاز به آبیاری دارد. فراموش نکنید!"
                data = {
                    "plant_id": str(plant.id),
                    "notification_type": "watering_reminder",
                    "plant_name": plant.name,
                }

                sent, error_msg = send_notification(token, title, body, data)

                if sent:
                    logger.debug(f"✅ اعلان FCM با موفقیت به توکن '{token}' برای گیاه {plant.name} ارسال شد.")
                else:
                    logger.error(
                        f"❌ ارسال اعلان FCM به توکن '{token}' برای گیاه {plant.name} (کاربر: {plant.user.username}) با خطا مواجه شد: {error_msg}"
                    )
                    if error_msg and (
                            "InvalidRegistrationToken" in error_msg or "NotRegistered" in error_msg or "BadDeviceToken" in error_msg):
                        fcm_device.is_active = False
                        fcm_device.save()
                        logger.warning(
                            f"⚠️ توکن FCM '{token}' برای کاربر '{plant.user.username}' غیرفعال شد (به دلیل نامعتبر بودن)."
                        )

            plant.mark_watered_today(note="Automated watering reminder sent via FCM")
            logger.info(
                f"گیاه {plant.name} برای کاربر {plant.user.username} پس از تلاش(های) اعلان FCM، به عنوان آبیاری شده علامت‌گذاری شد."
            )

        except Exception as fcm_e:
            logger.error(
                f"پردازش اعلان‌های FCM برای گیاه {plant.name} (کاربر: {plant.user.username}) با خطا مواجه شد: {fcm_e}",
                exc_info=True)
            try:
                self.retry(exc=fcm_e)
            except self.MaxRetriesExceededError:
                logger.error(f"حداکثر دفعات تلاش مجدد برای پردازش اعلان FCM برای گیاه {plant.name} از حد مجاز گذشت.")

    except Plant.DoesNotExist:
        logger.error(f"❌ گیاه با شناسه {plant_id} برای وظیفه آبیاری یافت نشد. نادیده گرفته شد.")
    except Exception as e:
        logger.error(f"❌ یک خطای غیرمنتظره در وظیفه water_plants برای شناسه گیاه {plant_id} رخ داد: {e}", exc_info=True)
        try:
            self.retry(exc=e)
        except self.MaxRetriesExceededError:
            logger.error(f"حداکثر دفعات تلاش مجدد برای وظیفه water_plants برای شناسه گیاه {plant_id} از حد مجاز گذشت.")