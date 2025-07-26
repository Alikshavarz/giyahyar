from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from django.utils import timezone
from .models import CustomUser
from .serializers import RegisterSerializer, LoginSerializer , CustomUserSerializer
from .utils import generate_otp, send_sms
from rest_framework_simplejwt.tokens import RefreshToken


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data)

class GuestFeatureView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        if not request.session.get('guest_used', False):
            request.session['guest_used'] = True
            return Response({"message": "دسترسی موفق به گیاه‌یار به عنوان میهمان."})
        return Response({"error": "فقط یکبار اجازه دسترسی دارید. لطفاً وارد شوید."}, status=403)


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            code = generate_otp()
            user.sms_code = code
            user.sms_code_expiry = timezone.now() + timezone.timedelta(minutes=5)
            user.save()
            send_sms(user.phone_number, code)
            return Response({"message": "ثبت‌نام انجام شد. کد تایید برای شما پیامک شد."})
        return Response(serializer.errors, status=400)


class VerifyPhoneView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        phone = request.data.get('phone_number')
        code = request.data.get('sms_code')
        user = CustomUser.objects.filter(phone_number=phone).first()
        if not user:
            return Response({"error": "کاربری با این شماره یافت نشد."}, status=404)
        if user.sms_code == code and user.sms_code_expiry and timezone.now() < user.sms_code_expiry:
            user.is_phone_verified = True
            user.sms_code = None
            user.sms_code_expiry = None
            user.save()
            return Response({"message": "شماره تایید شد."})
        return Response({"error": "کد نادرست یا منقضی."}, status=400)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data
        user = CustomUser.objects.filter(
            username=data.get('username_or_phone')
        ).first() or CustomUser.objects.filter(
            phone_number=data.get('username_or_phone')
        ).first()
        if not user:
            return Response({"error": "کاربر یافت نشد."}, status=404)
        if not user.check_password(data.get('password')):
            return Response({"error": "رمز اشتباه است."}, status=400)
        code = generate_otp()
        user.sms_code = code
        user.sms_code_expiry = timezone.now() + timezone.timedelta(minutes=5)
        user.save()
        send_sms(user.phone_number, code)
        return Response({'message': 'کد تایید ورود پیامک شد.'})


class LoginOTPVerify(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        phone = request.data.get('phone_number')
        code = request.data.get('sms_code')
        user = CustomUser.objects.filter(phone_number=phone).first()
        if not user:
            return Response({"error": "کاربر پیدا نشد."}, status=404)
        if user.sms_code == code and user.sms_code_expiry and timezone.now() < user.sms_code_expiry:
            user.is_phone_verified = True
            user.sms_code = None
            user.sms_code_expiry = None
            user.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "message": "ورود موفق و تایید شده."
            })
        return Response({"error":"کد نادرست یا منقضی"}, status=400)

from rest_framework.permissions import IsAuthenticated

class AuthFeatureView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
       
        if hasattr(user, "has_active_subscription") and user.has_active_subscription:
            return Response({"message": "دسترسی کامل به علت داشتن اشتراک فعال."})
        
        if user.feature_usage_count < 3:
            user.feature_usage_count += 1
            user.save()
            return Response({"message": f"اجازه شماره {user.feature_usage_count} برای استفاده از گیاه‌یار."})
        return Response({"error": "حداکثر ۳ بار حق استفاده! برای ادامه باید اشتراک بخرید."}, status=403)

# خروج
from rest_framework_simplejwt.tokens import RefreshToken

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'با موفقیت خارج شدید'})
        except Exception as e:
            return Response({'error': str(e)}, status=400)
