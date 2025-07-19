import requests
import base64
import os
import logging
from django.conf import settings

# اگر قصد دارید از Firebase برای FCM استفاده کنید، این خطوط را از حالت کامنت خارج کنید
# import firebase_admin
# from firebase_admin import credentials, messaging

# یک لاگر برای این ماژول تنظیم کنید
logger = logging.getLogger(__name__)

# --- کلید API از متغیرهای محیطی ---
# مطمئن شوید که PLANT_ID_API_KEY در محیط شما تنظیم شده است (مثلاً در فایل .env، تنظیمات سرور)
PLANT_ID_API_KEY = os.getenv("PLANT_ID_API_KEY")

# --- مسیر Credentials فایربیس (اگر از FCM استفاده می‌کنید) ---
# حتماً این را در فایل settings.py جنگو خود تعریف کنید اگر FCM را فعال می‌کنید
# مثال: FIREBASE_CREDENTIALS_PATH = os.path.join(BASE_DIR, 'path/to/your/serviceAccountKey.json')

# --- مقداردهی اولیه Firebase Admin SDK (اگر از FCM استفاده می‌کنید) ---
"""
# این بلوک را از حالت کامنت خارج کنید اگر FCM را فعال می‌کنید
if not firebase_admin._apps: # بررسی می‌کند که آیا SDK قبلاً مقداردهی اولیه شده است
    try:
        # بررسی کنید که آیا مسیر credential در settings تعریف شده است
        if hasattr(settings, 'FIREBASE_CREDENTIALS_PATH') and settings.FIREBASE_CREDENTIALS_PATH:
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase Admin SDK initialized successfully.")
        else:
            logger.warning("FIREBASE_CREDENTIALS_PATH not defined in settings. Firebase FCM will not be initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize Firebase Admin SDK: {e}")
"""


# =========================================================
# تابع تشخیص گیاه با استفاده از Plant.id API
# =========================================================
def diagnose_plant(image_field):
    """
    تصویری را برای تشخیص بیماری و دستورالعمل‌های مراقبت به Plant.id API ارسال می‌کند.

    ورودی:
        image_field: یک نمونه Django ImageField (مثلاً plant.image).

    خروجی:
        dict: یک دیکشنری شامل 'diagnosis', 'care_instructions', 'category',
              'confidence', و 'image' (همان ImageField اصلی).
              اگر تشخیص ناموفق بود یا داده معتبری پیدا نشد، None برمی‌گرداند.
    """
    if not PLANT_ID_API_KEY:
        logger.error("PLANT_ID_API_KEY تنظیم نشده است. نمی‌توان تشخیص گیاه را انجام داد.")
        return None

    if not image_field or not image_field.path:
        logger.warning("مسیر تصویر یا فیلد تصویر برای تشخیص ارائه نشده است.")
        return None

    image_path = image_field.path
    logger.info(f"تلاش برای تشخیص گیاه از تصویر: {image_path}")

    try:
        # تبدیل تصویر به base64
        with open(image_path, "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode("utf-8")

        # آماده‌سازی payload درخواست
        payload = {
            "api_key": PLANT_ID_API_KEY,
            "images": [img_base64],
            "modifiers": ["crops_fast", "similar_images"],  # این modifiers های خوبی هستند
            "plant_language": "fa",  # می‌توانید این را قابل تنظیم کنید یا از 'fa' (فارسی) در صورت پشتیبانی استفاده کنید
            "plant_details": ["common_names", "url", "wiki_description", "health_assessment"]
        }

        # ارسال درخواست به Plant.id API
        response = requests.post(
            "https://api.plant.id/v2/identify",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30  # برای جلوگیری از درخواست‌های معلق، یک timeout اضافه کنید
        )

        response.raise_for_status()  # برای پاسخ‌های بد (4xx یا 5xx) یک HTTPError ایجاد می‌کند
        data = response.json()
        logger.debug(f"پاسخ Plant.id API: {data}")

        # استخراج اطلاعات
        if not data or not data.get('suggestions'):
            logger.warning(f"هیچ پیشنهادی در پاسخ Plant.id API برای {image_path} یافت نشد. پاسخ: {data}")
            return {
                "diagnosis": "هیچ گیاه یا مشکل خاصی شناسایی نشد. لطفاً یک عکس واضح‌تر امتحان کنید.",
                "care_instructions": "گیاه خود را به دقت زیر نظر بگیرید.",
                "category": "other",
                "confidence": 0.0,
                "image": image_field
            }

        # تمرکز بر اولین پیشنهاد، با فرض اینکه مرتبط‌ترین است
        first_suggestion = data['suggestions'][0]
        plant_name = first_suggestion.get('plant_name', 'گیاه ناشناس')
        confidence = first_suggestion.get('probability', 0.0)

        diagnosis_text = f"شناسایی شده به عنوان: {plant_name}. "
        care_instructions_text = ""
        category_text = "other"  # دسته بندی پیش فرض

        health_assessment = data.get('health_assessment')
        if health_assessment and health_assessment.get('is_healthy', False):
            diagnosis_text += "گیاه شما سالم به نظر می‌رسد!"
            care_instructions_text = "روتین مراقبت عادی خود را ادامه دهید."
            category_text = "healthy"
        elif health_assessment and health_assessment.get('diseases'):
            diseases = health_assessment['diseases']
            if diseases:
                # گرفتن نام بیماری‌های شناسایی شده
                disease_names = [d.get('name', 'بیماری ناشناس') for d in diseases]
                diagnosis_text += f"بیماری‌های احتمالی شناسایی شده: {', '.join(disease_names)}. "

                # گرفتن درمان برای هر بیماری، یا یک پیام عمومی
                all_treatments = []
                for disease in diseases:
                    if disease.get('treatment'):
                        all_treatments.append(disease['treatment'])

                if all_treatments:
                    care_instructions_text = '\n'.join(all_treatments)
                else:
                    care_instructions_text = "برای درمان خاص با یک متخصص مشورت کنید."

                # تعیین دسته بندی بر اساس اولین بیماری در صورت وجود
                if diseases[0].get('classification'):
                    category_text = diseases[0]['classification']
                elif 'fungus' in disease_names[0].lower():
                    category_text = 'fungus'
                elif 'pest' in disease_names[0].lower() or 'insect' in disease_names[0].lower():
                    category_text = 'pest'
                else:
                    category_text = 'other'  # بازگشت به حالت پیش فرض برای دسته بندی ناشناس

            else:
                diagnosis_text += "هیچ بیماری خاصی شناسایی نشد با وجود اینکه ارزیابی سلامت مشکلاتی را پیشنهاد می‌کند. "
                care_instructions_text = "علائم را به دقت زیر نظر بگیرید."
        else:
            diagnosis_text += "ارزیابی سلامت قطعی نیست یا هیچ بیماری گزارش نشده است. "
            care_instructions_text = "علائم را به دقت زیر نظر بگیرید."

        return {
            "diagnosis": diagnosis_text.strip(),
            "care_instructions": care_instructions_text.strip(),
            "category": category_text,
            "confidence": round(confidence * 100, 2),  # درصد اطمینان
            "image": image_field  # ImageField اصلی را برمی‌گرداند
        }

    except requests.exceptions.HTTPError as http_err:
        logger.error(f"خطای HTTP هنگام تشخیص {image_path} رخ داد: {http_err} - پاسخ: {response.text}")
        return None
    except requests.exceptions.ConnectionError as conn_err:
        logger.error(f"خطای اتصال هنگام تشخیص {image_path} رخ داد: {conn_err}. آیا API قابل دسترسی است؟")
        return None
    except requests.exceptions.Timeout as timeout_err:
        logger.error(
            f"خطای مهلت زمانی هنگام تشخیص {image_path} رخ داد: {timeout_err}. API بیش از حد طول کشید تا پاسخ دهد.")
        return None
    except requests.exceptions.RequestException as req_err:
        logger.error(f"یک خطای درخواست غیرمنتظره هنگام تشخیص {image_path} رخ داد: {req_err}")
        return None
    except KeyError as ke:
        logger.error(
            f"خطای KeyError در تجزیه پاسخ Plant.id برای {image_path}: {ke}. ممکن است ساختار پاسخ تغییر کرده باشد. داده: {data}")
        return None
    except Exception as e:
        logger.error(f"یک خطای ناشناخته هنگام تشخیص گیاه برای {image_path} رخ داد: {e}", exc_info=True)
        return None


# =========================================================
# تابع ارسال اعلان FCM (اگر تصمیم به استفاده از Firebase دارید)
# =========================================================
"""
# این تابع را از حالت کامنت خارج کنید اگر FCM را فعال می‌کنید
def send_fcm_notification(fcm_token, title, body, data=None):
    
if not fcm_token:
    logger.warning("توکن FCM خالی است. نمی‌توان اعلان ارسال کرد.")
    return False

if not firebase_admin._apps:
    logger.error("Firebase Admin SDK مقداردهی اولیه نشده است. نمی‌توان اعلان FCM ارسال کرد.")
    return False

message = messaging.Message(
    notification=messaging.Notification(
        title=title,
        body=body,
    ),
    data=data,
    token=fcm_token,
)

try:
    response = messaging.send(message)
    logger.info(f"پیام FCM با موفقیت به {fcm_token} ارسال شد: {response}")
    return True
except Exception as e:
    logger.error(f"خطا در ارسال پیام FCM به {fcm_token}: {e}")
    return False
"""