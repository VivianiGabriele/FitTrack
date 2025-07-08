from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, UpdateView, CreateView, FormView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .forms import (
    CustomUserCreationForm,
    CustomAuthenticationForm,
    CustomUserChangeForm,
    CoachAssignmentForm,
    EndAssignmentForm,
    ClientProgressForm,
    CoachSelectionForm
)
from .models import CustomUser, ClientAssignment, CoachProfile, ClientProgress
from workouts.models import Workout
from goals.models import Goal, Measurement
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, DeleteView
from django.urls import reverse_lazy
from .models import ProgressComment, ClientProgress
from .forms import ProgressCommentForm
from django.db.models import Exists, OuterRef


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


class MyLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = "registration/login.html"


class UserProfileView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = "users/profile.html"
    success_url = reverse_lazy('profile')

    def get_object(self):
        return self.request.user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Ora il form accetta questo parametro
        return kwargs

# COACH VIEWS
class CoachDashboardView(ListView):
    template_name = 'users/coach/coach_dashboard.html'
    context_object_name = 'active_assignments'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        # Ottieni solo le assegnazioni attive per il coach loggato
        return ClientAssignment.objects.filter(
            coach=self.request.user,
            is_active=True
        ).select_related('client')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Aggiungi statistiche aggiuntive al contesto
        assignments = self.get_queryset()
        client_ids = [a.client_id for a in assignments]

        context['active_goals'] = Goal.objects.filter(
            user_id__in=client_ids,
            is_completed=False
        ).count()

        context['recent_workouts'] = Workout.objects.filter(
            user_id__in=client_ids
        ).count()

        return context

class CoachClientsListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'users/coach/clients_list.html'
    context_object_name = 'all_assignments'

    def test_func(self):
        return self.request.user.is_coach

    def get_queryset(self):
        return ClientAssignment.objects.filter(
            coach=self.request.user
        ).order_by('-is_active', '-date_assigned').select_related('client')

#passaggio dati per progressi visibili dal coach
class ClientDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = CustomUser
    template_name = 'users/coach/client_detail.html'
    context_object_name = 'client'

    def test_func(self):
        client = self.get_object()
        return self.request.user.is_coach and ClientAssignment.objects.filter(
            coach=self.request.user,
            client=client,
            is_active=True
        ).exists()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client = self.get_object()

        # Get active assignment
        assignment = get_object_or_404(
            ClientAssignment,
            client=client,
            coach=self.request.user,
            is_active=True
        )

        # Ottieni le misurazioni con annotazione per i commenti
        measurements = Measurement.objects.filter(user=client).annotate(
            has_comments=Exists(
                ProgressComment.objects.filter(
                    progress__measurement=OuterRef('pk'),
                    progress__assignment=assignment
                )
            )
        ).order_by('-date')

        # Prefetch dei commenti per ottimizzazione
        measurements = measurements.prefetch_related(
            'progress_report__comments__coach'
        )

        context.update({
            'workouts': Workout.objects.filter(user=client),
            'goals': Goal.objects.filter(user=client),
            'measurements': measurements,
            'assignment': assignment,
            'can_add_measurement': self.request.user.is_coach
        })
        return context

@login_required
def assign_client(request):
    if not request.user.is_coach:
        messages.warning(request, "Solo i coach possono assegnare clienti")
        return redirect('profile')

    if request.method == 'POST':
        form = CoachAssignmentForm(request.POST, coach=request.user)
        if form.is_valid():
            client = form.cleaned_data['client']

            # Create new assignment
            assignment = ClientAssignment.objects.create(
                coach=request.user,
                client=client,
                notes=form.cleaned_data.get('notes', ''),
                is_active=True
            )

            messages.success(request, f"{client.username} assegnato come tuo cliente")
            return redirect('coach_dashboard')
    else:
        form = CoachAssignmentForm(coach=request.user)

    return render(request, 'users/coach/assign-client.html', {
        'form': form,
        'active_tab': 'assign'
    })


@login_required
def end_assignment(request, assignment_id):
    if not request.user.is_coach:
        messages.warning(request, "Solo i coach possono gestire assegnazioni")
        return redirect('profile')

    assignment = get_object_or_404(
        ClientAssignment,
        pk=assignment_id,
        coach=request.user
    )

    if request.method == 'POST':
        form = EndAssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            assignment.end_assignment()
            messages.success(request, f"Assegnazione con {assignment.client.username} terminata")
            return redirect('coach_clients')
    else:
        form = EndAssignmentForm(instance=assignment)

    return render(request, 'users/coach/end_assignment.html', {
        'form': form,
        'assignment': assignment
    })


@login_required
def add_progress_report(request, client_id):
    if not request.user.is_coach:
        messages.warning(request, "Solo i coach possono aggiungere report")
        return redirect('profile')

    client = get_object_or_404(CustomUser, pk=client_id)
    assignment = get_object_or_404(
        ClientAssignment,
        coach=request.user,
        client=client,
        is_active=True
    )

    if request.method == 'POST':
        form = ClientProgressForm(request.POST)
        if form.is_valid():
            progress = form.save(commit=False)
            progress.assignment = assignment
            progress.save()
            messages.success(request, "Progresso registrato con successo")
            return redirect('client_detail', pk=client.id)
    else:
        form = ClientProgressForm()

    return render(request, 'users/coach/add_progress.html', {
        'form': form,
        'client': client
    })


# CLIENT VIEWS
class MyCoachView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = ClientAssignment
    template_name = 'client/my_coach.html'
    context_object_name = 'assignment'

    def test_func(self):
        return self.request.user.is_client

    def get_object(self):
        return get_object_or_404(
            ClientAssignment,
            client=self.request.user,
            is_active=True
        )


class MyProgressView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'client/my_progress.html'
    context_object_name = 'progress_reports'

    def test_func(self):
        return self.request.user.is_client

    def get_queryset(self):
        assignment = get_object_or_404(
            ClientAssignment,
            client=self.request.user,
            is_active=True
        )
        return ClientProgress.objects.filter(assignment=assignment).order_by('-date_recorded')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assignment'] = get_object_or_404(
            ClientAssignment,
            client=self.request.user,
            is_active=True
        )
        return context


# ADMIN VIEWS
class ManageAssignmentsView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'admin/manage_assignments.html'
    context_object_name = 'all_assignments'

    def test_func(self):
        return self.request.user.is_superuser

    def get_queryset(self):
        return ClientAssignment.objects.all().order_by('-is_active', '-date_assigned').select_related('coach', 'client')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_count'] = ClientAssignment.objects.filter(is_active=True).count()
        context['inactive_count'] = ClientAssignment.objects.filter(is_active=False).count()
        return context

@login_required
def select_coach(request):
    if not request.user.is_client:
        messages.warning(request, "Solo i clienti possono selezionare un coach")
        return redirect('profile')

    # Verifica se ha già un coach assegnato
    if ClientAssignment.objects.filter(client=request.user, is_active=True).exists():
        messages.info(request, "Hai già un coach assegnato")
        return redirect('my_coach')

    if request.method == 'POST':
        form = CoachSelectionForm(request.POST, client=request.user)
        if form.is_valid():
            coach = form.cleaned_data['coach']
            ClientAssignment.objects.create(
                coach=coach,
                client=request.user,
                is_active=True
            )
            messages.success(request, f"Hai selezionato il coach {coach.username}")
            return redirect('my_coach')
    else:
        form = CoachSelectionForm(client=request.user)

    return render(request, 'client/select_coach.html', {
        'form': form
    })

#vista commento coach



class AddProgressCommentView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = ProgressComment
    form_class = ProgressCommentForm
    template_name = 'users/add_progress_comment.html'

    def test_func(self):
        progress = ClientProgress.objects.get(pk=self.kwargs['progress_id'])
        return self.request.user.is_coach and self.request.user == progress.assignment.coach

    def form_valid(self, form):
        progress = ClientProgress.objects.get(pk=self.kwargs['progress_id'])
        form.instance.progress = progress
        form.instance.coach = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('client_detail', kwargs={'pk': self.object.progress.assignment.client.pk})


class DeleteProgressCommentView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = ProgressComment
    template_name = 'users/delete_progress_comment.html'

    def test_func(self):
        return self.request.user == self.get_object().coach

    def get_success_url(self):
        return reverse_lazy('client_detail', kwargs={'pk': self.object.progress.assignment.client.pk})