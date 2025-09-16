from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Project, Progress
from profiles.models import UserProfile

User = get_user_model()

class ProgressTrackerTestCase(TestCase):
    def setUp(self):
        # Create recruiter and candidate
        self.recruiter = User.objects.create_user(
            username="recruiter",
            password="pass123", 
            role="recruiter",
            phone="1234569890" 
            )
        self.candidate = User.objects.create_user(
            username="candidate",
            password="pass123",
            email='candidate@example.com',
            role="candidate",
            phone="1234567890"  # must be unique
            )

        # Create profiles
        self.recruiter_profile = UserProfile.objects.create(user=self.recruiter)
        self.candidate_profile = UserProfile.objects.create(user=self.candidate)
        
        # Create a project
        self.project = Project.objects.create(
            project_name="Test Project",
            client=self.recruiter,
            user=self.recruiter,  # <-- required field
            status="in_progress"
        )


    def test_project_progress_view_requires_login(self):
        url = reverse("project_progress", args=[self.project.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_project_progress_view_as_candidate(self):
        self.client.login(username="candidate", password="pass123")
        url = reverse("project_progress", args=[self.project.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "progress_tracker/project_progress.html")
        self.assertIn("progress_data", response.context)

    def test_update_progress_view_permission_denied_for_unfinished_previous_stage(self):
        self.client.login(username="candidate", password="pass123")
        # Create two progress stages
        stage1 = Progress.objects.create(project=self.project, stage="Stage 1", user=self.candidate, is_completed=False)
        stage2 = Progress.objects.create(project=self.project, stage="Stage 2", user=self.candidate, is_completed=False)

        url = reverse("update_progress", args=[stage2.id])
        response = self.client.get(url)
        self.assertContains(response, "You must complete previous stages before updating this one.")

    def test_update_project_status_view_as_non_recruiter(self):
        self.client.login(username="candidate", password="pass123")
        url = reverse("update_project_status", args=[self.project.id])
        response = self.client.get(url)
        self.assertRedirects(response, reverse("project_progress", args=[self.project.id]))
    
    def test_update_project_status_view_as_recruiter(self):
        self.client.login(username="recruiter", password="pass123")
        url = reverse("update_project_status", args=[self.project.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "progress_tracker/update_project_status.html")

    def test_confirm_progress_view_as_non_recruiter(self):
        self.client.login(username="candidate", password="pass123")
        progress = Progress.objects.create(project=self.project, stage="Stage 1", user=self.candidate, is_completed=True)
        url = reverse("confirm_progress", args=[progress.id])
        response = self.client.post(url)
        self.assertRedirects(response, reverse("project_progress", args=[self.project.id]))

    def test_confirm_progress_view_as_recruiter(self):
        self.client.login(username="recruiter", password="pass123")
        progress = Progress.objects.create(project=self.project, stage="Stage 1", user=self.candidate, is_completed=True)
        url = reverse("confirm_progress", args=[progress.id])
        response = self.client.post(url)
        progress.refresh_from_db()
        self.assertTrue(progress.client_confirmation)
        self.assertRedirects(response, reverse("project_progress", args=[self.project.id]))
