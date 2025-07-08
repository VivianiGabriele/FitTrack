from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import CustomUser, ClientAssignment, CoachProfile, ClientProgress
from django.conf import settings


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email", "age", "description", "role")


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email", "age", "description", "role")

    def __init__(self, *args, **kwargs):
        # Rimuovi 'user' da kwargs prima di chiamare il parent __init__
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Aggiungi qui eventuali logiche basate sull'utente

class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ("username", "password")

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age < 18:
            raise ValidationError("You must be 18 years or older to log in.")
        return age

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise ValidationError("This account is inactive.", code="inactive")
        if user.username.startswith("b"):
            raise ValidationError("Sorry, accounts starting with 's' aren't welcome here.", code="no_b_users")


class CoachAssignmentForm(forms.ModelForm):
    class Meta:
        model = ClientAssignment
        fields = ['client', 'notes']
        widgets = {
            'client': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.coach = kwargs.pop('coach', None)
        super().__init__(*args, **kwargs)

        # Filtra solo utenti standard non già assegnati
        if self.coach:
            assigned_client_ids = ClientAssignment.objects.filter(
                is_active=True
            ).values_list('client_id', flat=True)

            self.fields['client'].queryset = CustomUser.objects.filter(
                role='standard'
            ).exclude(
                id__in=assigned_client_ids
            )


class EndAssignmentForm(forms.ModelForm):
    class Meta:
        model = ClientAssignment
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Motivazione della chiusura...'
            })
        }


class ClientProgressForm(forms.ModelForm):
    class Meta:
        model = ClientProgress
        fields = ['weight', 'body_fat_percentage', 'performance_rating', 'notes']
        widgets = {
            'weight': forms.NumberInput(attrs={'class': 'form-control'}),
            'body_fat_percentage': forms.NumberInput(attrs={'class': 'form-control'}),
            'performance_rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10
            }),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class CoachSelectionForm(forms.Form):
    coach = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(role='coach'),
        label="Seleziona un coach",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        self.client = kwargs.pop('client', None)
        super().__init__(*args, **kwargs)

        # Filtra coach che non hanno già questo client assegnato
        if self.client and self.client.assignments_as_client.filter(is_active=True).exists():
            current_coach = self.client.assignments_as_client.filter(is_active=True).first().coach
            self.fields['coach'].queryset = CustomUser.objects.filter(
                role='coach'
            ).exclude(
                id=current_coach.id
            )

#form commento coach
from django import forms
from .models import ProgressComment

class ProgressCommentForm(forms.ModelForm):
    class Meta:
        model = ProgressComment
        fields = ['comment', 'is_private']
        widgets = {
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Inserisci il tuo commento...'
            }),
            'is_private': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'is_private': 'Commento privato (visibile solo al coach)'
        }