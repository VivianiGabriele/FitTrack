#users/urls.py
from django.urls import path
from .views import SignUpView, MyLoginView, UserProfileView,CoachDashboardView,ClientDetailView
from . import views
from .views import AddProgressCommentView, DeleteProgressCommentView
from .views import add_progress_report
from goals.views import add_measurement
urlpatterns = [
    # Autenticazione
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', views.MyLoginView.as_view(), name='login'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),

    # URL per i Coach
    path('coach/dashboard/', views.CoachDashboardView.as_view(), name='coach_dashboard'),
    path('coach/clients/', views.CoachClientsListView.as_view(), name='coach_clients'),
    path('coach/client/<int:pk>/', views.ClientDetailView.as_view(), name='client_detail'),
    path('coach/assign-client/', views.assign_client, name='assign_client'),
    path('coach/end-assignment/<int:assignment_id>/', views.end_assignment, name='end_assignment'),
    path('coach/add-progress/<int:client_id>/', views.add_progress_report, name='add_progress'),

    # URL per i Clienti
    path('client/my-coach/', views.MyCoachView.as_view(), name='my_coach'),
    path('client/my-progress/', views.MyProgressView.as_view(), name='my_progress'),
    path('client/select-coach/', views.select_coach, name='select_coach'),

    # URL Admin (opzionali)
    path('admin/assignments/', views.ManageAssignmentsView.as_view(), name='manage_assignments'),
    #commento coach
    path('progress/<int:progress_id>/comment/add/',
         AddProgressCommentView.as_view(),
         name='add_progress_comment'),
    path('comment/<int:pk>/delete/',
         DeleteProgressCommentView.as_view(),
         name='delete_progress_comment'),
    path('client/<int:client_id>/add-progress/', add_progress_report, name='add_progress_report'),
    path('client/<int:client_id>/add-measurement/', add_measurement, name='add_measurement'),
]