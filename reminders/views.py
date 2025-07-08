from django.shortcuts import render

# Create your views here.
# reminders/views.py
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import WorkoutReminder

@login_required
def dismiss_reminder(request):
    reminder = WorkoutReminder.objects.get(user=request.user)
    reminder.show_reminder = False
    reminder.save()
    return JsonResponse({'status': 'success'})