from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('standard', 'Standard User'),
        ('coach', 'Coach'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='standard')
    description = models.TextField(blank=True, default='')
    age = models.PositiveIntegerField(default=30)
    registration_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Utente'
        verbose_name_plural = 'Utenti'
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_coach(self):
        return self.role == 'coach'

    @property
    def is_client(self):
        return self.role == 'standard'

    def get_active_coach(self):
        """Restituisce il coach attualmente assegnato"""
        assignment = self.assignments_as_client.filter(is_active=True).first()
        return assignment.coach if assignment else None

    def get_active_clients(self):
        """Restituisce i clienti attualmente assegnati (per coach)"""
        return CustomUser.objects.filter(
            assignments_as_client__coach=self,
            assignments_as_client__is_active=True
        )

    def get_all_assignments(self):
        """Restituisce tutte le assegnazioni (storico)"""
        if self.is_coach:
            return self.assignments_as_coach.all()
        else:
            return self.assignments_as_client.all()


    def get_active_assignments(self):
        """Per coach: restituisce le assegnazioni attive"""
        if self.is_coach:
            return ClientAssignment.objects.filter(coach=self, is_active=True)
        return ClientAssignment.objects.none()

    def get_active_clients(self):
        """Per coach: restituisce i clienti attivi"""
        if self.is_coach:
            return CustomUser.objects.filter(
                assignments_as_client__coach=self,
                assignments_as_client__is_active=True
            )
        return CustomUser.objects.none()

class CoachProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='coach_profile'
    )
    bio = models.TextField(blank=True)
    specialization = models.CharField(max_length=100, blank=True)
    certifications = models.TextField(blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Profilo Coach"
        verbose_name_plural = "Profili Coach"

    def __str__(self):
        return f"Profilo Coach di {self.user.username}"


class ClientAssignment(models.Model):
    coach = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='assignments_as_coach',
        limit_choices_to={'role': 'coach'},
        on_delete=models.CASCADE
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='assignments_as_client',
        limit_choices_to={'role': 'standard'},
        on_delete=models.CASCADE
    )
    date_assigned = models.DateTimeField(auto_now_add=True)
    date_ended = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Assegnazione Cliente"
        verbose_name_plural = "Assegnazioni Clienti"
        constraints = [
            models.UniqueConstraint(
                fields=['client'],
                condition=models.Q(is_active=True),
                name='unique_active_client_assignment'
            )
        ]
        ordering = ['-date_assigned']

    def __str__(self):
        status = "attivo" if self.is_active else "storico"
        return f"{self.client} assegnato a {self.coach} ({status})"

    def save(self, *args, **kwargs):
        # Disattiva altre assegnazioni attive per questo client
        if self.is_active:
            ClientAssignment.objects.filter(
                client=self.client,
                is_active=True
            ).exclude(pk=self.pk).update(
                is_active=False,
                date_ended=timezone.now()
            )
        super().save(*args, **kwargs)

    def end_assignment(self):
        """Metodo per terminare un'assegnazione"""
        self.is_active = False
        self.date_ended = timezone.now()
        self.save()


class ClientProgress(models.Model):
    """Modello opzionale per tracciare i progressi dei clienti"""
    assignment = models.ForeignKey(
        ClientAssignment,
        related_name='progress_reports',
        on_delete=models.CASCADE
    )
    date_recorded = models.DateTimeField(auto_now_add=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    body_fat_percentage = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    notes = models.TextField(blank=True)
    performance_rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Valutazione da 1 a 10"
    )
    measurement = models.OneToOneField(
        'goals.Measurement',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='progress_report')
    class Meta:
        verbose_name = "Progresso Cliente"
        verbose_name_plural = "Progressi Clienti"
        ordering = ['-date_recorded']

    def __str__(self):
        return f"Progresso di {self.assignment.client} ({self.date_recorded.date()})"



#commento da parte del coach
class ProgressComment(models.Model):
    """Modello per i commenti dei coach sui progressi dei clienti"""
    progress = models.ForeignKey(
        ClientProgress,
        related_name='comments',
        on_delete=models.CASCADE
    )
    coach = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='progress_comments',
        limit_choices_to={'role': 'coach'},
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    comment = models.TextField()
    is_private = models.BooleanField(
        default=False,
        help_text="Se privato, visibile solo al coach e non al cliente"
    )

    class Meta:
        verbose_name = "Commento Progresso"
        verbose_name_plural = "Commenti Progressi"
        ordering = ['-created_at']

    def __str__(self):
        return f"Commento di {self.coach.username} su {self.progress.assignment.client.username} ({self.created_at.date()})"