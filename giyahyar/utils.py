import requests
import base64
import os
from django.conf import settings

PLANT_ID_API_KEY = os.getenv("PLANT_ID_API_KEY")  # کلید API را از محیط بخوان

def diagnose_plant(image_field):
    """
    ارسال تصویر به API و دریافت تشخیص بیماری و راهکار مراقبتی
    """
    image_path = image_field.path

    # تبدیل تصویر به base64
    with open(image_path, "rb") as img_file:
        img_base64 = base64.b64encode(img_file.read()).decode()

    # ارسال درخواست به API
    response = requests.post(
        "https://api.plant.id/v2/identify",
        headers={"Content-Type": "application/json"},
        json={
            "api_key": PLANT_ID_API_KEY,
            "images": [img_base64],
            "modifiers": ["crops_fast", "similar_images"],
            "plant_language": "en",
            "plant_details": ["common_names", "url", "wiki_description", "health_assessment"]
        }
    )

    if response.status_code != 200:
        return None

    data = response.json()

    try:
        # استخراج اطلاعات از پاسخ
        plant_name = data['suggestions'][0]['plant_name']
        health = data['health_assessment']['diseases']
        diagnosis = ', '.join([d['name'] for d in health])
        care = '\n'.join([d.get('treatment', 'No treatment provided') for d in health])
        category = health[0].get('classification', 'other')
        confidence = data['suggestions'][0].get('probability', 0.0)

        return {
            "diagnosis": diagnosis,
            "care_instructions": care,
            "category": category,
            "confidence": round(confidence * 100, 2),  # درصد اطمینان
            "image": image_field  # همان تصویر اصلی
        }

    except Exception as e:
        print("Diagnosis error:", e)
        return None
