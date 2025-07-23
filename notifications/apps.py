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

            cred_path = os.getenv('FIREBASE_CREDENTIAL_PATH', 'firebase/firebase_key.json')

            if not firebase_admin._apps:
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                logger.info("✅ Firebase Admin SDK initialized successfully.")
            else:
                logger.info("🔄 Firebase Admin SDK was already initialized.")

        except ImportError:
            logger.error("❌ The 'firebase-admin' library is not installed. Run: pip install firebase-admin")
        except FileNotFoundError:
            logger.error(f"❌ Credential file not found at: {cred_path}")
        except Exception as e:
            logger.error(f"🔥 Failed to initialize Firebase Admin SDK: {e}")