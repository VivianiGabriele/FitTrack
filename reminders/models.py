from django.db import models

# Create your models here.
# reminders/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


# reminders/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class WorkoutReminder(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    last_checked = models.DateTimeField(auto_now_add=True)
    show_reminder = models.BooleanField(default=False)
    reminder_message = models.TextField(blank=True)

    def __str__(self):
        return f"Reminder for {self.user.username}"