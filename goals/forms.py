from django import forms
from .models import Goal
from .models import Measurement

class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ['date', 'weight', 'body_fat', 'muscle_mass', 'water_percentage', 'calories', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'body_fat': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'muscle_mass': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'water_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'calories': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class MeasurementForm(forms.ModelForm):
    class Meta:
        model = Measurement
        fields = ['date', 'weight', 'body_fat', 'muscle_mass', 'water_percentage', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'body_fat': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'muscle_mass': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'water_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }