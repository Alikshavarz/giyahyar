import base64
import requests
import logging
from django.core.files.images import ImageFile

logger = logging.getLogger(__name__)

class PlantDiagnosisService:
    def __init__(self, image_field, api_key):
        self.image_field = image_field  # باید instance یک ImageField باشه
        self.api_key = api_key
        self.image_path = getattr(image_field, 'path', None)

    def encode_image(self):
        with open(self.image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def build_payload(self, image_base64):
        return {
            "api_key": self.api_key,
            "images": [image_base64],
            "modifiers": ["crops_fast", "similar_images"],
            "plant_language": "fa",
            "plant_details": ["common_names", "url", "wiki_description", "health_assessment"]
        }

    def call_api(self, payload):
        try:
            response = requests.post(
                "https://api.plant.id/v2/identify",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"❌ Plant.id request failed: {e}", exc_info=True)
            return None

    def diagnose(self):
        if not self.image_path:
            logger.warning("تصویر یا مسیر تصویر معتبر نیست.")
            return None

        try:
            base64_img = self.encode_image()
            payload = self.build_payload(base64_img)
            result = self.call_api(payload)
            return result
        except Exception as e:
            logger.error(f"❌ خطای داخلی در diagnosis: {e}", exc_info=True)
            return None


