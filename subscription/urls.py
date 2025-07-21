from django.urls import path
from . import views

urlpatterns = [
    path('', views.SubscriptionListView.as_view()),                    # GET /api/subscription
    path('buy/', views.SubscriptionCreateView.as_view()),              # POST /api/subscription/buy
    path('<int:pk>/', views.SubscriptionDeleteView.as_view()),         # DELETE /api/subscription/<pk>
    path('plans/', views.PlanListView.as_view()),                      # GET /api/subscription/plans
    path('history/', views.PaymentHistoryListView.as_view()),          # GET /api/subscription/history
    path('stats/', views.SubscriptionStatsView.as_view()),             # GET /api/subscription/stats
]
