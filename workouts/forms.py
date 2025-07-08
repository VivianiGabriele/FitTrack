#models/forms.py
from django import forms
from .models import Workout
from django.core.validators import MinValueValidator

class WorkoutForm(forms.ModelForm):
    class Meta:
        model = Workout
        fields = ['date', 'duration', 'exercises', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': 'Seleziona data'
            }),
            'duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Durata in minuti',
                'min': 1
            }),
            'exercises': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Esercizi svolti (separati da virgola)'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Note aggiuntive...'
            }),
        }
        labels = {
            'date': 'Data allenamento',
            'duration': 'Durata (minuti)',
            'exercises': 'Esercizi svolti',
            'notes': 'Note'
        }

    def clean_duration(self):
        duration = self.cleaned_data.get('duration')
        if duration and duration < 1:
            raise forms.ValidationError("La durata deve essere almeno 1 minuto")
        return duration