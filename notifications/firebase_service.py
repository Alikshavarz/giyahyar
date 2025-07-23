import logging
import os
import firebase_admin
from firebase_admin import credentials, messaging
from decouple import config


logger = logging.getLogger(__name__)

SERVICE_ACCOUNT_PATH = config('FIREBASE_CREDENTIAL_PATH', default='firebase/giyahyar-9eeca-firebase-adminsdk-fbsvc-4e41e5aeda.json')
FCM_SERVER_KEY = config('FCM_SERVER_KEY', default='')
TARGET_TOKEN = config('FCM_TARGET_TOKEN', default='')
NOTIFICATION_TITLE = config('NOTIFICATION_TITLE', default='پیام جدید از سودم')
NOTIFICATION_BODY = config('NOTIFICATION_BODY', default='شما یک پیام مهم دارید!')


def initialize_firebase():
    if not firebase_admin._apps:
        try:
            cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
            firebase_admin.initialize_app(cred)
            logger.info("✅ Firebase initialized")
        except Exception as e:
            logger.error(f"❌ Firebase initialization failed: {e}")
    else:
        logger.info("🔄 Firebase was already initialized")


def send_notification(token, title, body, data=None):
    initialize_firebase()

    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data or {},
            token=token if not token.startswith("/topics/") else None,
            topic=token[8:] if token.startswith("/topics/") else None,
        )

        response = messaging.send(message)
        logger.info(f"✅ Message sent successfully to {token}: {response}")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to send message to {token}: {e}", exc_info=True)
        return False

config("FIREBASE_CREDENTIAL_PATH")