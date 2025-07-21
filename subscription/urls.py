from django.urls import path
from .views import (
    SubscriptionListCreateView, SubscriptionDeleteView,
    PlanListView, PaymentHistoryListView, SubscriptionStatsView
)
urlpatterns = [
    path('', SubscriptionListCreateView.as_view()),                    # GET, POST /api/subscription/
    path('<int:pk>/', SubscriptionDeleteView.as_view()),               # DELETE /api/subscription/<pk>/        
    path('plans/', PlanListView.as_view()),                            # GET /api/subscription/plans/
    path('history/', PaymentHistoryListView.as_view()),                # GET /api/subscription/history/
    path('stats/', SubscriptionStatsView.as_view()),                   # GET /api/subscription/stats/
]




         
                        
              
             