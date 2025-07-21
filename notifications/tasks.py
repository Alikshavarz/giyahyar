#  است Firebase این تسک مسئول ارسال پیام به


from celery import shared_task
from plants.models import Plant
from .models import FCMDevice
import logging
import firebase_admin
from firebase_admin import messaging, credentials

logger = logging.getLogger(__name__)

# مطمئن شوید که مسیر فایل JSON مربوط به Firebase Admin SDK را به درستی وارد کرده‌اید.
# این فایل باید در محیط تولید (production) در مکانی امن قرار گیرد.
try:
    cred = credentials.Certificate("firebase/giyahyar-9eeca-firebase-adminsdk-fbsvc-4e41e5aeda.json")
    firebase_admin.initialize_app(cred)
except ValueError:
    logger.warning("Firebase app already initialized.")
except Exception as e:
    logger.error(f"Failed to initialize Firebase Admin SDK: {e}")


@shared_task
def water_plants(plant_id):
    """
    تسک Celery برای ارسال اعلان آبیاری برای یک گیاه خاص.
    """
    try:
        # اطلاعات گیاه را از اپلیکیشن plant دریافت می‌کنیم
        plant = Plant.objects.get(id=plant_id)
        logger.info(f"Preparing to send watering notification for plant: {plant.name} (ID: {plant.id})")

        # توکن FCM کاربر را از مدل FCMDevice در همین اپلیکیشن می‌گیریم
        try:
            fcm_device = FCMDevice.objects.get(user=plant.user)
            token = fcm_device.registration_id

            message = messaging.Message(
                notification=messaging.Notification(
                    title=f"زمان آبیاری {plant.name}!",
                    body=f"گیاه زیبای {plant.name} نیاز به آبیاری دارد. فراموش نکنید!"
                ),
                token=token,
            )

            response = messaging.send(message)
            logger.debug(f"✅ Message sent successfully: {response}")

            logger.info(
                f"FCM notification sent for plant {plant.name} to user {plant.user.username}. Response: {response}")

        except FCMDevice.DoesNotExist:
            logger.warning(f"No FCM token found for user {plant.user.username} (Plant: {plant.name}).")
        except Exception as fcm_e:
            logger.error(f"Failed to send FCM notification for plant {plant.name}: {fcm_e}")

    except Plant.DoesNotExist:
        logger.error(f"Plant with ID {plant_id} not found for watering task.")
    except Exception as e:
        logger.error(f"An error occurred in water_plants task for plant ID {plant_id}: {e}")