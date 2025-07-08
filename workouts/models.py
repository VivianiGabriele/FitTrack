#workouts/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model()

class Workout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workouts')
    name = models.CharField(
        max_length=100,
        default="Allenamento",
        verbose_name="Nome allenamento"
    )
    date = models.DateField(verbose_name="Data allenamento")
    duration = models.PositiveIntegerField(
        verbose_name="Durata (min)",
        default=0,
        validators=[MinValueValidator(1)],
        help_text="Durata in minuti"
    )
    exercises = models.TextField(
        verbose_name="Esercizi svolti",
        default="Riscaldamento, Squat, Affondi",
        help_text="Separare gli esercizi con virgole"
    )
    notes = models.TextField(verbose_name="Note aggiuntive", blank=True, null=True)

    class Meta:
        ordering = ['-date']
        verbose_name = "Allenamento"
        verbose_name_plural = "Allenamenti"

    def __str__(self):
        return f"{self.name} - {self.date.strftime('%d/%m/%Y')}"


class Meta:
    ordering = ['-date']