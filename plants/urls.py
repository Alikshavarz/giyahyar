from django.urls import path
from .views import (
    PlantListCreateView,
    PlantRetrieveUpdateDestroyView,
    PlantDiagnosisCreateWithAIView,
    PlantDiagnosisListView,
    PlantDiagnosisRetrieveUpdateDestroyView,
    WateringLogCreateView,
    WateringLogListView,
    WateringScheduleListCreateView,
    WateringScheduleListCreateView,
)

urlpatterns = [

    path('plants/', PlantListCreateView.as_view(), name='plant-list-create'),

    path('plants/<int:pk>/', PlantRetrieveUpdateDestroyView.as_view(), name='plant-retrieve-update-destroy'),

    path('plants/<int:pk>/diagnose/', PlantDiagnosisCreateWithAIView.as_view(), name='plant-diagnose-create'),

    path('diagnoses/', PlantDiagnosisListView.as_view(), name='diagnosis-list'),

    path('diagnoses/<int:pk>/', PlantDiagnosisRetrieveUpdateDestroyView.as_view(), name='diagnosis-retrieve-update-destroy'),

    path('plants/<int:pk>/water/', WateringLogCreateView.as_view(), name='wateringlog-create'),

    path('plants/<int:pk>/watering-logs/', WateringLogListView.as_view(), name='wateringlog-list'),

    path('watering-schedules/', WateringScheduleListCreateView.as_view(), name='watering-schedule-list-create'),

    path('watering-schedules/<int:pk>/', WateringScheduleListCreateView.as_view(), name='watering-schedule-retrieve-update-destroy'),
]