from django.urls import path
from .views import (
    GuestFeatureView, RegisterView, VerifyPhoneView, LoginView,
    LoginOTPVerify, AuthFeatureView, LogoutView, UserProfileView, LoginWithUsernameView
)

urlpatterns = [
    path('guest-feature/', GuestFeatureView.as_view()),
    path('register/', RegisterView.as_view()),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('verify-phone/', VerifyPhoneView.as_view()),
    path('login/', LoginView.as_view()),
    path('user-login/', LoginWithUsernameView.as_view()),
    path('login-otp/', LoginOTPVerify.as_view()),
    path('use-feature/', AuthFeatureView.as_view()),
    path('logout/', LogoutView.as_view())
]
