from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from profiles.models import UserProfile
from services.models import Service
from talents.models import Skills
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
import json

User = get_user_model()

class TalentViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Dummy user
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword123",
            email="testuser@test.com"
        )

        # Profile with image
        self.profile = UserProfile.objects.create(
            user=self.user,
            skills="python, django",
            profile_image=SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        )

        # Service
        self.service = Service.objects.create(
            name="Web Development",
            skills="python, django"
        )

        # Skill
        self.skill = Skills.objects.create(skill="Python")

    def test_talent_view_page_loads(self):
        response = self.client.get(reverse("talents"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "talents/talents.html")
        self.assertIn("total_skills", response.context)
        self.assertContains(response, str(self.skill.skill))

    def test_fetch_skill_data(self):
        response = self.client.get(reverse("fetch_skill_data", args=[self.skill.id]))
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertIn("random_skill", data)
        self.assertEqual(data["random_skill"], "Python")
        self.assertTrue(any(s["name"] == "Web Development" for s in data["related_services"]))

    def test_skill_service_candidates(self):
        response = self.client.get(reverse("skill_service_candidates", args=[self.service.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "services/candidates.html")
        self.assertContains(response, self.user.username)
