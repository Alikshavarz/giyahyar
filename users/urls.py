from django.urls import path
from .views import (
    RegisterView, CustomLoginView, ProfileView, GuestUseView,
    UseFeatureView, LogoutView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('guest-use/', GuestUseView.as_view(), name='guest-use'),
    path('use-feature/', UseFeatureView.as_view(), name='use-feature'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
