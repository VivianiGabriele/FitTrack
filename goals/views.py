#goals/views.py
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from pyexpat.errors import messages
from django.contrib.auth.decorators import login_required
from users.models import CustomUser
from .models import Goal
from .forms import GoalForm
from django.views.generic import ListView
import json
from django.utils import timezone
from django.shortcuts import render, redirect
from .models import Measurement
from .forms import MeasurementForm
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

def goal_list(request):
    goals = Goal.objects.filter(user=request.user).order_by('date')
    latest_measurements = Measurement.objects.filter(user=request.user).order_by('-date')[:10]  # Ultime 10 misurazioni

    # Prepara i dati per i grafici
    weight_labels = [goal.date.strftime('%Y-%m-%d') for goal in goals if goal.weight]
    weight_values = [float(goal.weight) for goal in goals if goal.weight]

    fat_labels = [goal.date.strftime('%Y-%m-%d') for goal in goals if goal.body_fat]
    fat_values = [float(goal.body_fat) for goal in goals if goal.body_fat]

    context = {
        'goals': goals,
        'latest_measurements': latest_measurements,  # Aggiunto questo
        'weight_labels': json.dumps(weight_labels),  # Convertito in JSON
        'weight_values': json.dumps(weight_values),
        'fat_labels': json.dumps(fat_labels),
        'fat_values': json.dumps(fat_values),
    }

    return render(request, 'goal_list.html', context)


class GoalListView(ListView):
    model = Goal
    template_name = 'goal_list.html'
    context_object_name = 'goals'

    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user).order_by('date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get measurements ordered by date
        measurements = Measurement.objects.filter(
            user=self.request.user
        ).order_by('date')

        # Get goals ordered by date
        goals = Goal.objects.filter(
            user=self.request.user
        ).order_by('date')

        # Prepare measurement data
        measurement_data = []
        for m in measurements:
            if m.weight or m.body_fat:
                measurement_data.append({
                    'date': m.date.strftime('%Y-%m-%d'),
                    'weight': float(m.weight) if m.weight else None,
                    'fat': float(m.body_fat) if m.body_fat else None
                })

        # Prepare goal data
        goal_data = []
        for g in goals:
            if g.weight or g.body_fat:
                goal_data.append({
                    'date': g.date.strftime('%Y-%m-%d'),
                    'weight': float(g.weight) if g.weight else None,
                    'fat': float(g.body_fat) if g.body_fat else None
                })

        # Create aligned data for charts
        weight_labels = []
        weight_values = []
        weight_goals = []

        fat_labels = []
        fat_values = []
        fat_goals = []

        # Process weight data
        for m in measurement_data:
            if m['weight'] is not None:
                weight_labels.append(m['date'])
                weight_values.append(m['weight'])

                # Find closest goal for this measurement date
                closest_goal = None
                for g in goal_data:
                    if g['weight'] is not None and g['date'] >= m['date']:
                        closest_goal = g['weight']
                        break

                weight_goals.append(closest_goal)

        # Process fat data
        for m in measurement_data:
            if m['fat'] is not None:
                fat_labels.append(m['date'])
                fat_values.append(m['fat'])

                # Find closest goal for this measurement date
                closest_goal = None
                for g in goal_data:
                    if g['fat'] is not None and g['date'] >= m['date']:
                        closest_goal = g['fat']
                        break

                fat_goals.append(closest_goal)

        # Add to context
        context['weight_labels'] = json.dumps(weight_labels)
        context['weight_values'] = json.dumps(weight_values)
        context['weight_goals'] = json.dumps(weight_goals)

        context['fat_labels'] = json.dumps(fat_labels)
        context['fat_values'] = json.dumps(fat_values)
        context['fat_goals'] = json.dumps(fat_goals)

        # Add latest measurements
        context['latest_measurements'] = measurements.order_by('-date')[:10]

        # Add coach comments if available
        active_assignment = ClientAssignment.objects.filter(
            client=self.request.user,
            is_active=True
        ).first()

        if active_assignment:
            context['comments'] = ProgressComment.objects.filter(
                progress__assignment=active_assignment,
                user=self.request.user
            ).order_by('-created_at')
            context['active_assignment'] = active_assignment

        return context

class GoalCreateView(LoginRequiredMixin, CreateView):
    model = Goal
    form_class = GoalForm
    template_name = 'goals/goal_form.html'
    success_url = reverse_lazy('goal_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class GoalUpdateView(LoginRequiredMixin, UpdateView):
    model = Goal
    form_class = GoalForm
    template_name = 'goals/goal_form.html'
    success_url = reverse_lazy('goal_list')

    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user)


class GoalDeleteView(LoginRequiredMixin, DeleteView):
    model = Goal
    template_name = 'goals/goal_confirm_delete.html'
    success_url = reverse_lazy('goal_list')

    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user)


class MeasurementCreateView(LoginRequiredMixin, CreateView):
    model = Measurement
    form_class = MeasurementForm
    template_name = 'goals/add_measurement.html'
    success_url = reverse_lazy('goal_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        print(f"Misurazione salvata - ID: {self.object.id}, Utente: {self.object.user.username}")
        return response

class MeasurementUpdateView(LoginRequiredMixin, UpdateView):
    model = Measurement
    form_class = MeasurementForm
    template_name = 'goals/add_measurement.html'
    success_url = reverse_lazy('goal_list')

    def get_queryset(self):
        return Measurement.objects.filter(user=self.request.user)

class MeasurementDeleteView(LoginRequiredMixin, DeleteView):
    model = Measurement
    template_name = 'goals/measurement_confirm_delete.html'
    success_url = reverse_lazy('goal_list')

    def get_queryset(self):
        return Measurement.objects.filter(user=self.request.user)


@login_required
def add_measurement(request, client_id):
    if not request.user.is_coach:
        messages.warning(request, "Only coaches can add measurements")
        return redirect('profile')

    client = get_object_or_404(CustomUser, pk=client_id)

    if request.method == 'POST':
        form = MeasurementForm(request.POST)
        if form.is_valid():
            measurement = form.save(commit=False)
            measurement.user = client
            measurement.save()
            messages.success(request, "Measurement added successfully")
            return redirect('client_detail', pk=client.id)
    else:
        form = MeasurementForm()

    return render(request, 'goals/add_measurement.html', {
        'form': form,
        'client': client
    })


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Measurement, Goal
from users.models import CustomUser, ProgressComment, ClientProgress, ClientAssignment
from users.forms import ProgressCommentForm


@login_required
def client_measurements(request, client_id):
    """
    View per visualizzare le misurazioni di un cliente con possibilità di commentare
    """
    client = get_object_or_404(CustomUser, pk=client_id)

    # Verifica che l'utente sia il coach assegnato OPPURE il cliente stesso
    is_client_viewing = (request.user == client)

    if not is_client_viewing:
        if not request.user.is_coach or not ClientAssignment.objects.filter(
                coach=request.user,
                client=client,
                is_active=True
        ).exists():
            messages.warning(request, "You are not authorized to view this page")
            return redirect('coach_dashboard' if request.user.is_coach else 'profile')

    # Ottieni l'assegnazione attiva
    active_assignment = ClientAssignment.objects.filter(
        client=client,
        is_active=True
    ).first()

    measurements = Measurement.objects.filter(user=client).order_by('-date')

    measurement_forms = []
    for measurement in measurements:
        # Crea o recupera il progress report associato
        progress, created = ClientProgress.objects.get_or_create(
            measurement=measurement,
            defaults={
                'assignment': active_assignment,
                'date_recorded': measurement.date
            }
        )

        # Ottieni i commenti visibili
        if is_client_viewing:
            # Per il cliente: solo commenti pubblici o del suo coach attuale
            comments = ProgressComment.objects.filter(
                progress=progress
            ).filter(
                Q(is_private=False) |
                Q(coach=active_assignment.coach) if active_assignment else Q()
            ).select_related('coach').order_by('-created_at')
        else:
            # Per il coach: tutti i commenti
            comments = ProgressComment.objects.filter(
                progress=progress
            ).select_related('coach').order_by('-created_at')

        measurement_forms.append({
            'measurement': measurement,
            'comment_form': ProgressCommentForm(),
            'comments': comments,
            'progress_id': progress.id,
            'can_comment': request.user.is_coach and not is_client_viewing
        })

    return render(request, 'templates/goals/goal_list.html', {
        'client': client,
        'measurement_forms': measurement_forms,
        'can_comment': request.user.is_coach and not is_client_viewing,
        'is_client_viewing': is_client_viewing,
        'active_assignment': active_assignment
    })


from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Measurement
from users.models import ClientProgress, ProgressComment


@login_required
def add_measurement_comment(request, measurement_id):
    measurement = get_object_or_404(Measurement, pk=measurement_id)

    if not request.user.is_coach:
        messages.warning(request, "Only coaches can add comments")
        return redirect('client_detail', pk=measurement.user.id)

    # Crea o recupera il progress report associato
    progress, created = ClientProgress.objects.get_or_create(
        measurement=measurement,
        defaults={
            'assignment': request.user.assignments_as_coach.filter(is_active=True).first(),
            'date_recorded': measurement.date
        }
    )

    if request.method == 'POST':
        comment = request.POST.get('comment', '').strip()
        is_private = request.POST.get('is_private', False) == 'on'

        if comment:
            ProgressComment.objects.create(
                progress=progress,
                coach=request.user,
                comment=comment,
                is_private=is_private
            )
            messages.success(request, "Comment added successfully")
        else:
            messages.warning(request, "Comment cannot be empty")

    return redirect('client_detail', pk=measurement.user.id)
