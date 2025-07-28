from django.urls import path
from . import views

urlpatterns = [
    # پلن‌ها را برمی‌گرداند
    path('plans/', views.PlansView.as_view(), name='subscription-plans'),

    # خرید اشتراک - فقط post
    path('buy/', views.SubscriptionBuyView.as_view(), name='buy-renew-subscription'),

    # تاریخچه پرداخت کاربر جاری
    path('my-payments/', views.PaymentHistoryView.as_view(), name='my-payment-history'),

    # لیست نوتیفیکیشن‌های کاربر
    path('my-notifications/', views.NotificationListView.as_view(), name='my-notifications'),

    # یادآوری اتمام اشتراک
    path('remember/', views.RememberSubscriptionAPIView.as_view(), name='remember-subscription'),

    # بخش مدیریتی (admin)
    path('admin/plans/', views.AdminPlans.as_view(), name='admin-plans'),  # لیست و ایجاد پلن جدید (get-post)
    # چون در AdminPlans برای update/delete متد put و delete دادی، اما پارامتر pk را توی url نیاز داری:
    path('admin/plans/<int:pk>/', views.AdminPlans.as_view(), name='admin-plan-detail'),

    path('admin/payments/', views.AdminPayments.as_view(), name='admin-payments'),
    path('admin/stats/', views.AdminOverview.as_view(), name='admin-stats'),
]
