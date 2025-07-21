from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'

    def ready(self):
        """
        این متد زمانی فراخوانی می‌شود که جنگو برنامه را بارگذاری می‌کند.
        مقداردهی اولیه Firebase را در اینجا انجام می‌دهیم.
        """
        try:
            import firebase_admin
            from firebase_admin import credentials

            cred = credentials.Certificate('firebase/giyahyar-9eeca-firebase-adminsdk-fbsvc-4e41e5aeda.json')

            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred)
                logger.info("Firebase Admin SDK initialized successfully.")
            else:
                logger.info("Firebase Admin SDK was already initialized.")
        except ImportError:
            logger.error("The 'firebase-admin' library is not installed. Please run: pip install firebase-admin")
        except Exception as e:
            logger.error(f"Failed to initialize Firebase Admin SDK: {e}")