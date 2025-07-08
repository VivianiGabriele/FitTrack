#users/tests.py
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class UsersManagersTests(TestCase):
    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpass1234",
            role="standard"  # Aggiunto il campo role
        )
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.role, "standard")  # Test per il ruolo
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser(
            username="testsuperuser",
            email="testsuperuser@example.com",
            password="testpass1234",
            role="coach"  # Aggiunto il campo role
        )
        self.assertEqual(admin_user.role, "coach")  # Verifica il ruolo
        self.assertTrue(admin_user.is_superuser)

    # NUOVI TEST PER LE FUNZIONALITÀ COACH
    def test_coach_assignment(self):
        User = get_user_model()

        # Crea un coach
        coach = User.objects.create_user(
            username="testcoach",
            password="coachpass123",
            role="coach"
        )

        # Crea un utente standard con coach assegnato
        user = User.objects.create_user(
            username="testclient",
            password="clientpass123",
            role="standard",
            coach=coach  # Assegna il coach
        )

        self.assertEqual(user.coach, coach)
        self.assertEqual(coach.clients.count(), 1)  # Verifica la relazione inversa

    def test_coach_dashboard_access(self):
        User = get_user_model()

        # Crea un utente coach
        coach = User.objects.create_user(
            username="coachuser",
            password="testpass123",
            role="coach"
        )

        # Crea un utente standard (non coach)
        normal_user = User.objects.create_user(
            username="normaluser",
            password="testpass123",
            role="standard"
        )

        # Test accesso alla dashboard coach
        self.client.login(username="coachuser", password="testpass123")
        response = self.client.get(reverse("coach_dashboard"))
        self.assertEqual(response.status_code, 200)

        # Verifica che un utente normale non possa accedere
        self.client.login(username="normaluser", password="testpass123")
        response = self.client.get(reverse("coach_dashboard"))
        self.assertEqual(response.status_code, 403)  # Dovrebbe essere proibito


class SignupPageTests(TestCase):
    # ... (mantieni i test esistenti che hai già) ...

    def test_signup_with_role(self):
        """Test che verifica la registrazione con campo role"""
        response = self.client.post(
            reverse("signup"),
            {
                "username": "testuser2",
                "email": "test2@email.com",
                "password1": "testpass123",
                "password2": "testpass123",
                "role": "coach"  # Campo aggiuntivo
            },
        )
        self.assertEqual(response.status_code, 302)
        user = get_user_model().objects.get(username="testuser2")
        self.assertEqual(user.role, "coach")