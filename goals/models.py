from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from datetime import date
from django.core.validators import MinValueValidator
from decimal import Decimal

from users.models import ClientProgress, ClientAssignment
from workouts.models import Workout

User = get_user_model()


class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True,
                                 blank=True)  # Cambiato da FloatField a DecimalField
    body_fat = models.DecimalField(max_digits=4, decimal_places=1, null=True,
                                   blank=True)  # Cambiato da FloatField a DecimalField
    muscle_mass = models.DecimalField(max_digits=5, decimal_places=2, null=True,
                                      blank=True)  # Cambiato da FloatField a DecimalField
    water_percentage = models.DecimalField(max_digits=4, decimal_places=1, null=True,
                                           blank=True)  # Cambiato da FloatField a DecimalField
    notes = models.TextField(null=True, blank=True)
    calories = models.IntegerField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    @property
    def muscle_progress(self):
        from .models import Measurement
        measurements = Measurement.objects.filter(user=self.user, date__lte=self.date).order_by('-date')
        if measurements.exists() and self.muscle_mass:
            latest = measurements.first().muscle_mass
            if latest and self.muscle_mass:
                progress = float(latest) / float(self.muscle_mass) * 100
                return (latest, min(100, int(progress)))
        return None

    @property
    def weight_progress(self):
        from .models import Measurement
        measurements = Measurement.objects.filter(user=self.user, date__lte=self.date).order_by('-date')
        if measurements.exists() and self.weight:
            latest = measurements.first().weight
            if latest and self.weight:
                # Converti entrambi i valori a float prima della divisione
                progress = float(latest) / float(self.weight) * 100
                return (latest, min(100, int(progress)))
        return None

    @property
    def water_progress(self):
        from .models import Measurement
        measurements = Measurement.objects.filter(user=self.user, date__lte=self.date).order_by('-date')
        if measurements.exists() and self.water_percentage:
            latest = measurements.first().water_percentage
            if latest and self.water_percentage:
                progress = float(latest) / float(self.water_percentage) * 100
                return (latest, min(100, int(progress)))
        return None

    @property
    def fat_progress(self):
        from .models import Measurement
        measurements = Measurement.objects.filter(user=self.user, date__lte=self.date).order_by('-date')
        if measurements.exists() and self.body_fat:
            latest = measurements.first().body_fat
            if latest and self.body_fat:
                progress = float(latest) / float(self.body_fat) * 100
                return (latest, min(100, int(progress)))
        return None

    @property
    def overall_progress(self):
        progresses = []
        if self.weight_progress:
            progresses.append(self.weight_progress[1])
        if self.fat_progress:
            progresses.append(self.fat_progress[1])
        if self.muscle_progress:
            progresses.append(self.muscle_progress[1])
        if self.water_progress:
            progresses.append(self.water_progress[1])

        if progresses:
            return sum(progresses) // len(progresses)
        return None

    def get_goal_description(self):
        descriptions = []
        if self.weight:
            descriptions.append(f"Peso: {self.weight}kg")
        if self.body_fat:
            descriptions.append(f"Grasso: {self.body_fat}%")
        if self.muscle_mass:
            descriptions.append(f"Muscoli: {self.muscle_mass}kg")
        if self.water_percentage:
            descriptions.append(f"Acqua: {self.water_percentage}%")

        return " | ".join(descriptions) if descriptions else "Obiettivo generico"

    def __str__(self):
        return f"Obiettivo del {self.date.strftime('%d/%m/%Y')} - {self.get_goal_description()}"


class Measurement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True,
                                 blank=True)  # Cambiato da FloatField a DecimalField
    body_fat = models.DecimalField(max_digits=4, decimal_places=1, null=True,
                                   blank=True)  # Cambiato da FloatField a DecimalField
    muscle_mass = models.DecimalField(max_digits=5, decimal_places=2, null=True,
                                      blank=True)  # Cambiato da FloatField a DecimalField
    water_percentage = models.DecimalField(max_digits=4, decimal_places=1, null=True,
                                           blank=True)  # Cambiato da FloatField a DecimalField
    notes = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-date']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client = self.get_object()

        # Get active assignment
        assignment = ClientAssignment.objects.filter(
            client=client,
            coach=self.request.user,
            is_active=True
        ).first()

        # Get measurements from goals app
        try:
            from goals.models import Measurement
            measurements = Measurement.objects.filter(user=client).order_by('-date')
        except:
            measurements = []

        context.update({
            'workouts': Workout.objects.filter(user=client),
            'goals': Goal.objects.filter(user=client),
            'measurements': measurements,  # Aggiunto questo
            'assignment': assignment,
            'progress_reports': ClientProgress.objects.filter(assignment=assignment).order_by('-date_recorded')
        })
        return context
    @property
    def progress_report(self):
        """Restituisce il ClientProgress associato a questa misurazione"""
        from users.models import ClientProgress
        return ClientProgress.objects.filter(measurement=self).first()


#class Goal(models.Model):
#    user = models.ForeignKey(User, on_delete=models.CASCADE)
#    title = models.CharField(max_length=100)
#    target_value = models.FloatField()
#    current_value = models.FloatField(default=0)
#    created_at = models.DateTimeField(auto_now_add=True)
#    deadline = models.DateField()
#    is_completed = models.BooleanField(default=False)
#
#à    def __str__(self):
#        return f"{self.title} - {self.user.username}"

#    class Meta:
#        ordering = ['-created_at']


