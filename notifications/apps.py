from django.apps import AppConfig
import logging
import os

logger = logging.getLogger("notifications")

class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'

    def ready(self):
        self.initialize_firebase()

    def initialize_firebase(self):

        try:
            import firebase_admin
            from firebase_admin import credentials

            cred_path = os.getenv('FIREBASE_CREDENTIAL_PATH', 'firebase/giyahyar-9eeca-firebase-adminsdk-fbsvc-4e41e5aeda.json')

            if not firebase_admin._apps:
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                logger.info("✅ Firebase Admin SDK با موفقیت مقداردهی اولیه شد.")
            else:
                logger.info("🔄 Firebase Admin SDK قبلاً مقداردهی اولیه شده است.")

        except ImportError:
            logger.error("❌ کتابخانه 'firebase-admin' نصب نیست. لطفا اجرا کنید: pip install firebase-admin")
        except FileNotFoundError:
            logger.error(f"❌ فایل اعتبارسنجی در مسیر: {cred_path} یافت نشد.")
        except Exception as e:
            logger.error(f"🔥 خطایی در مقداردهی اولیه Firebase Admin SDK رخ داد: {e}")