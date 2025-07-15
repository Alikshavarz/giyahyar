from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


# Swagger/OpenAPI schema configuration
schema_view = get_schema_view(
    openapi.Info(
        title="Plant Guardian API",
        default_version='v1',
        description="API documentation for the Plant Care application",
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/plants/', include('plants.urls')),
    path('api/users/', include('users.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# اضافه کردن مسیر فایل‌های رسانه‌ای (تصاویر و...)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
