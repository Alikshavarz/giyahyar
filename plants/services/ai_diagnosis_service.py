import base64
import requests
import logging
from django.core.files.images import ImageFile
import json

logger = logging.getLogger(__name__)

class PlantDiagnosisService:
    def __init__(self, image_field, api_key):
        self.image_field = image_field
        self.api_key = api_key
        self.image_path = getattr(image_field, 'path', None)

    def encode_image(self):
        if not self.image_path:
            raise ValueError("Image path is not valid for encoding.")
        try:
            with open(self.image_path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except FileNotFoundError:
            raise FileNotFoundError(f"Image file not found at {self.image_path}")
        except Exception as e:
            raise Exception(f"Error encoding image: {e}")

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
        except requests.exceptions.Timeout:
            logger.error("❌ Plant.id request timed out.", exc_info=True)
            raise Exception("AI service connection timed out.")
        except requests.exceptions.ConnectionError:
            logger.error("❌ Could not connect to Plant.id service.", exc_info=True)
            raise Exception("Could not connect to AI diagnosis service.")
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"❌ Plant.id service returned an HTTP error: {http_err} - {response.text}", exc_info=True)
            raise Exception(f"AI service returned an error: {http_err} - {response.text}")
        except json.JSONDecodeError:
            logger.error("❌ Plant.id service returned an invalid JSON response.", exc_info=True)
            raise Exception("AI service returned an invalid JSON response.")
        except requests.RequestException as e:
            logger.error(f"❌ Plant.id request failed: {e}", exc_info=True)
            raise Exception(f"An unexpected request error occurred: {e}")
        except Exception as e:
            logger.error(f"❌ An unexpected error occurred during API call: {e}", exc_info=True)
            raise Exception(f"An unexpected error occurred: {e}")

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
            raise