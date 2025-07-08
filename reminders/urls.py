# reminders/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('dismiss-reminder/', views.dismiss_reminder, name='dismiss_reminder'),
]