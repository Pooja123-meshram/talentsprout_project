from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages

from .models import UserProfile, ProjectExperience, SocialLink, PrivacyPolicy, EducationDetail
from progress_tracker.models import Project, ProjectDetails, ProgressStage
from payment.models import Payment

from django.conf import settings
from urllib.parse import quote

User = get_user_model()

class ProfileViewsTestCase(TestCase):
    def setUp(self):
        # Create a recruiter
        self.recruiter = User.objects.create_user(
        username="recruiter",
        password="pass123",
        role="recruiter",
        email="recruiter@example.com",

        phone="1111111111"  # unique phone
        )
        
        # Create a candidate
        self.candidate = User.objects.create_user(
        username="candidate",
        password="pass123",
        role="candidate",
        phone="2222222222"  # different phone
        )

        # Create profiles
        self.recruiter_profile = UserProfile.objects.create(user=self.recruiter)
        self.candidate_profile = UserProfile.objects.create(user=self.candidate)

        # Create project details
        self.project_details = ProjectDetails.objects.create(
            project_name="Test Project",
            recruiter=self.recruiter,
            candidate=self.candidate
        )

        # Create privacy policy entry
        self.privacy_policy = PrivacyPolicy.objects.create(content="Test policy.")

    def test_profiles_view_requires_login(self):
        url = reverse("profiles")
        response = self.client.get(url)
        expected_login_url = f"{settings.LOGIN_URL}?next={quote(url)}"
        self.assertRedirects(response, expected_login_url, fetch_redirect_response=False)

    def test_profiles_view_as_candidate(self):
        self.client.login(username="candidate", password="pass123")
        response = self.client.get(reverse("profiles"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profiles/profiles.html")
        self.assertIn("user_profile", response.context)

  





    def test_add_project_experience(self):
        self.client.login(username="candidate", password="pass123")
        
        url = reverse("add_project")
        response = self.client.post(url, {
            "title": "Test Project",
            "contribution":"contribution",
            "description": "Test description",
            "technologies":"technologies",
            "duration":"duration",
            "project_number":"1"
     
        })
        
        print(response.status_code)
        print(response.content.decode())  # to see any validation errors

        self.assertEqual(response.status_code, 302)  # Redirect after success


    def test_update_project_status(self):
        self.client.login(username="candidate", password="pass123")
        url = reverse("update_project_status", args=[self.project_details.id, "accept"])
        response = self.client.get(url)
        self.project_details.refresh_from_db()
        self.assertEqual(self.project_details.candidate_status, "accepted")

    def test_privacy_policy_view(self):
        self.client.login(username="candidate", password="pass123")
        response = self.client.get(reverse("privacy_policy"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test policy.")

    def test_add_progress_stage_as_recruiter(self):
        self.client.login(username="recruiter", password="pass123")
        url = reverse("add_progress_stage_view", args=[self.project_details.id])
        data = {
            "title": "Stage 1",
            "description": "Stage description"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ProgressStage.objects.filter(title="Stage 1").exists())

    def test_mark_stage_completed_by_candidate(self):
        stage = ProgressStage.objects.create(
            title="Stage 1",
            description="desc",
            project_detail=self.project_details
        )
        self.client.login(username="candidate", password="pass123")
        url = reverse("mark_stage_completed", args=[stage.id])
        data = {
            "title": "Stage 1",
            "description": "desc"
        }
        response = self.client.post(url, data)
        stage.refresh_from_db()
        self.assertTrue(stage.is_completed)

    def test_confirm_stage_completion_by_recruiter(self):
        stage = ProgressStage.objects.create(
            title="Stage 1",
            description="desc",
            project_detail=self.project_details,
            is_completed=True
        )
        self.client.login(username="recruiter", password="pass123")
        url = reverse("confirm_stage_completion_view", args=[stage.id])
        response = self.client.get(url)
        stage.refresh_from_db()
        self.assertTrue(stage.confirmed_by_recruiter)
