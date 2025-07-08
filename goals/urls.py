from django.urls import path
from .views import GoalListView, GoalCreateView, GoalUpdateView, GoalDeleteView, MeasurementUpdateView,MeasurementDeleteView
from . import views
from django.urls import include
from .views import (
    goal_list,
    GoalCreateView,
    GoalUpdateView,
    GoalDeleteView,
    MeasurementCreateView  # Importa la class-based view
)
urlpatterns = [
    path('', GoalListView.as_view(), name='goal_list'),  # Usa la class-based view
    path('add/', GoalCreateView.as_view(), name='add_goal'),
    path('edit/<int:pk>/', GoalUpdateView.as_view(), name='edit_goal'),
    path('delete/<int:pk>/', GoalDeleteView.as_view(), name='delete_goal'),
    path('measurements/add/', MeasurementCreateView.as_view(), name='add_measurement'),
    path('measurements/edit/<int:pk>/', MeasurementUpdateView.as_view(), name='edit_measurement'),
    path('measurements/delete/<int:pk>/', MeasurementDeleteView.as_view(), name='delete_measurement'),
    path('measurement/<int:measurement_id>/comment/', views.add_measurement_comment, name='add_measurement_comment'),
    path('', include('reminders.urls')),
]