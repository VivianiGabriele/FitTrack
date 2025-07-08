"""
URL configuration for FitTrack project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from workouts import views
from users.views import CoachDashboardView
from .views import HomeView

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    # Authentication
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/", include("users.urls")),

    # Workouts App (unico endpoint)
    path("workouts/", include("workouts.urls")),

    # Pages App
    path("", include("pages.urls")),
    path('goals/', include('goals.urls')),
    path('workout/<int:user_id>/', views.workout_view, name='user_workout'),
    path('coach/dashboard/', CoachDashboardView.as_view(), name='coach_dashboard'),

]
