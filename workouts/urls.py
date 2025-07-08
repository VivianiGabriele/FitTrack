from django.urls import path
from .views import (
    WorkoutListView,
    WorkoutCreateView,
    WorkoutUpdateView,
    WorkoutDeleteView
)

urlpatterns = [
    path('', WorkoutListView.as_view(), name='workout_list'),
    path('new/', WorkoutCreateView.as_view(), name='workout_create'),
    path('<int:pk>/edit/', WorkoutUpdateView.as_view(), name='workout_update'),
    path('<int:pk>/delete/', WorkoutDeleteView.as_view(), name='workout_delete'),
]