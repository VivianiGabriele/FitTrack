from django.views.generic import TemplateView
from workouts.models import Workout
from goals.models import Goal
from django.utils import timezone


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            # Ultimi 3 allenamenti (ultimi 7 giorni)
            recent_date = timezone.now() - timezone.timedelta(days=7)
            context['recent_workouts'] = Workout.objects.filter(
                user=self.request.user,
                date__gte=recent_date
            ).order_by('-date')[:3]

            # Obiettivi attivi (non completati)
            context['active_goals'] = Goal.objects.filter(
                user=self.request.user,
                is_completed=False
            ).order_by('-date')[:3]

            # Progresso medio per la dashboard
            if context['active_goals']:
                context['average_progress'] = sum(
                    goal.overall_progress or 0
                    for goal in context['active_goals']
                ) / len(context['active_goals'])

        return context