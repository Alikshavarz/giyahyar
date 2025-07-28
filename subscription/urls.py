from django.urls import path
from .views import (
    PlansView, BuySubscriptionView, MyPaymentsView, MyNotificationsView,
    SendReminderView, AdminPlansView, AdminPlanDetailView, AdminPaymentsView, AdminStatsView
)

urlpatterns = [
    path('plans/', PlansView.as_view()),
    path('buy/', BuySubscriptionView.as_view()),
    path('my-payments/', MyPaymentsView.as_view()),
    path('my-notifications/', MyNotificationsView.as_view()),
    path('remember/', SendReminderView.as_view()),

    path('admin/plans/', AdminPlansView.as_view()),
    path('admin/plans/<int:pk>/', AdminPlanDetailView.as_view()),
    path('admin/payments/', AdminPaymentsView.as_view()),
    path('admin/stats/', AdminStatsView.as_view())
]
