#pages/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

class HomePageView(TemplateView):
    template_name = "home.html"
