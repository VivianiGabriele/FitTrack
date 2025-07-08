# reminders/middleware.py
import logging
from datetime import timedelta
from django.utils import timezone
from workouts.models import Workout
from reminders.models import WorkoutReminder

logger = logging.getLogger(__name__)


class WorkoutReminderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            one_week_ago = timezone.now() - timedelta(days=7)
            reminder, created = WorkoutReminder.objects.get_or_create(user=request.user)

            # Controlla se l'utente ha MAI fatto workout (nuovo criterio)
            has_any_workout = Workout.objects.filter(user=request.user).exists()

            # Solo se ha fatto almeno un workout in passato
            if has_any_workout:
                has_recent_workouts = Workout.objects.filter(
                    user=request.user,
                    date__gte=one_week_ago,
                    date__lte=timezone.now()
                ).exists()

                if not has_recent_workouts:
                    reminder.show_reminder = True
                    reminder.reminder_message = "Non hai registrato allenamenti nell'ultima settimana! 💪"
                else:
                    reminder.show_reminder = False
            else:
                reminder.show_reminder = False  # Non mostrare a nuovi utenti

            reminder.last_checked = timezone.now()
            reminder.save()
            request.workout_reminder = reminder

        return self.get_response(request)