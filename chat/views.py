from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
import requests
from django.conf import settings
from .models import Message
from .serializers import MessageSerializer


GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash-002:generateContent"

CUSTOM_PROMPT = (
    "توی پیام ها تا زمانی که از تو خواسته نشده نگو کی هستی"
    "تو هوش مصنوعی مخصوص اپلیکیشن گیاه یار هستی. "
    "خودت را هرگز Gemini یا هیچ مدل دیگر هوش مصنوعی معرفی نکن! "
    "تو توسط تیم برنامه نویسی نکست لول در ایران ساخته شدی"
    "گیاه یار یک اپ برای نگهداری و مراقبت گل و گیاهان است"
)

class ChatAPIView(APIView):
    permission_classes = [permissions.AllowAny]  

    def post(self, request):
        user_message = request.data.get('message', '').strip()
        if not user_message:
            return Response({'error': 'متن پیام اجباری است.'}, status=status.HTTP_400_BAD_REQUEST)

        full_prompt = f"{CUSTOM_PROMPT}\n\n{user_message}"

        data = {
            "contents": [
                {
                    "parts": [
                        {"text": full_prompt}
                    ]
                }
            ]
        }
        try:
            gemini_response = requests.post(
                f"{GEMINI_API_URL}?key={settings.GEMINI_API_KEY}",
                headers={"Content-Type": "application/json"},
                json=data,
                timeout=20
            )
            if gemini_response.status_code == 200:
                g_response = gemini_response.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "پاسخی دریافت نشد.")
                
                msg = Message.objects.create(user=request.user if request.user.is_authenticated else None,
                                            text=user_message, response=g_response)
                return Response({'answer': g_response, 'chat': MessageSerializer(msg).data})
            else:
                return Response({'error': 'خطا در ارتباط با هوش مصنوعی گیاه یار.', 'detail': gemini_response.text}, status=gemini_response.status_code)
        except Exception as e:
            return Response({'error': 'ارتباط با سرور چت بات ممکن نشد.', 'detail': str(e)}, status=500)
