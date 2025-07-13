from rest_framework import serializers
from .models import CustomUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class RegisterSerializer(serializers.ModelSerializer):
    """Serializer برای ثبت‌نام (Sign Up)"""
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'password', 'phone_number', 'email']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user

class UserSerializer(serializers.ModelSerializer):
    """نمایش اطلاعات کاربر"""
    has_active_subscription = serializers.ReadOnlyField()
    class Meta:
        model = CustomUser
        fields = [
            'id', 'first_name', 'last_name', 'username', 'phone_number', 'email',
            'usage_count', 'has_active_subscription', 'subscription_end'
        ]

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
   
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        token['usage_count'] = user.usage_count
        token['has_active_subscription'] = user.has_active_subscription
        return token
