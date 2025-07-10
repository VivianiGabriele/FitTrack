#workout/views.py
from django.http import HttpResponse
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from .models import Workout
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from .forms import WorkoutForm
from django.views.generic import DeleteView
from django.core.exceptions import PermissionDenied

class WorkoutListView(LoginRequiredMixin, ListView):
    model = Workout
    template_name = 'workouts/workout_list.html'
    context_object_name = 'workouts'

    def get_queryset(self):
        """Filtra solo gli allenamenti dell'utente corrente"""
        return super().get_queryset().filter(user=self.request.user)

class WorkoutCreateView(LoginRequiredMixin, CreateView):
    model = Workout
    form_class = WorkoutForm  # Usa il form che hai definito invece di fields
    template_name = 'workouts/workout_form.html'
    success_url = reverse_lazy('workout_list')  # Aggiungi l'URL di successo

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

def index(request):
    return HttpResponse("Benvenuto nella pagina workout!")

class WorkoutDeleteView(DeleteView):
    model = Workout
    template_name = 'workouts/workout_confirm_delete.html'
    success_url = reverse_lazy('workout_list')

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
@login_required
def workout_view(request, user_id=None):
    template_name = 'users/coach/coach_dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_coach:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clients'] = self.request.user.clients.all()
        return context

@login_required
def coach_dashboard(request):
    if not request.user.is_coach:
        raise PermissionDenied

    return render(request, 'users/coach/coach_dashboard.html', {
        'clients': request.user.clients.all()
    })



class WorkoutUpdateView(LoginRequiredMixin, UpdateView):
    model = Workout
    form_class = WorkoutForm
    template_name = 'workouts/workout_form.html'
    success_url = reverse_lazy('workout_list')

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


