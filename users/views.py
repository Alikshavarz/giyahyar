from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import CustomUser
from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer, UserSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView

class RegisterView(generics.CreateAPIView):
    """ثبت‌ نام کاربر"""
    serializer_class = RegisterSerializer

class CustomLoginView(TokenObtainPairView):
    
    serializer_class = CustomTokenObtainPairSerializer

class ProfileView(generics.RetrieveAPIView):
    """نمایش پروفایل کاربر (باید لاگین کرده باشد)"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

class GuestUseView(APIView):
    
    def post(self, request):
        if request.session.get('guest_used', False):
            return Response({'detail': 'شما فقط یکبار به عنوان مهمان مجاز به استفاده هستید.'},
                            status=status.HTTP_403_FORBIDDEN)
        request.session['guest_used'] = True
        return Response({'detail': 'موفق! این اولین و آخرین بار استفاده مهمان است.'})

class UseFeatureView(APIView):
    """
    استفاده کاربر عضو از امکانات   
    """
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        user = request.user
        
        if user.has_active_subscription:
            return Response({'detail': 'امکان استفاده نامحدود برای اشتراک فعال!'})
        
        if user.usage_count >= 3:
            return Response({'detail': 'سقف استفاده شما به اتمام رسیده.'}, status=status.HTTP_403_FORBIDDEN)
     
        user.increment_usage()
        return Response({'detail': f'تائید! استفاده شما: {user.usage_count}/3'})

class LogoutView(APIView):
   
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        return Response({'detail': '!شما با موفقیت خارج شدید'})
