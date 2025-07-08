# reminders/management/commands/check_inactive_users.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from workouts.models import Workout
from users.models import CustomUser
from datetime import timedelta


class Command(BaseCommand):
    help = 'Invia email di promemoria agli utenti inattivi'

    def handle(self, *args, **options):
        # Data di una settimana fa
        one_week_ago = timezone.now() - timedelta(days=7)

        # Ottieni tutti gli utenti attivi
        active_users = CustomUser.objects.filter(is_active=True)

        for user in active_users:
            # Verifica se ha fatto workout nell'ultima settimana
            has_workouts = Workout.objects.filter(
                user=user,
                date__gte=one_week_ago
            ).exists()

            if not has_workouts:
                self.send_reminder_email(user)

    def send_reminder_email(self, user):
        subject = "🔔 Promemoria FitTrack - Riprendi i tuoi allenamenti!"
        message = render_to_string('reminders/email/workout_reminder.txt', {
            'user': user,
        })

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        self.stdout.write(f"Email inviata a {user.email}")