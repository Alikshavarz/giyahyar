# -------------------[ Configurable Variables ]-------------------
SERVICE_ACCOUNT_PATH = "firebase/giyahyar-9eeca-firebase-adminsdk-fbsvc-4e41e5aeda.json"
TARGET_TOKEN = "DEVICE_TOKEN_OR_TOPIC"         # می‌تونه توکن یا "/topics/topic_name" باشه
NOTIFICATION_TITLE = "پیام جدید از سودم"
NOTIFICATION_BODY = "شما یک پیام مهم دارید!"
# ---------------------------------------------------------------

import firebase_admin
from firebase_admin import credentials, messaging

def initialize_firebase():
    cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred)

def send_notification():
    message = messaging.Message(
        notification=messaging.Notification(
            title=NOTIFICATION_TITLE,
            body=NOTIFICATION_BODY,
        ),
        token=TARGET_TOKEN if not TARGET_TOKEN.startswith("/topics/") else None,
        topic=TARGET_TOKEN[8:] if TARGET_TOKEN.startswith("/topics/") else None,
    )

    response = messaging.send(message)
    print("✅ Successfully sent message:", response)

if __name__ == "__main__":
    initialize_firebase()
    send_notification()
