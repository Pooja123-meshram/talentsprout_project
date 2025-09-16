from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import Service, Service_page, ServiceRequest
from profiles.models import UserProfile

User = get_user_model()


class ServiceModelTest(TestCase):
    def test_service_str(self):
        service = Service.objects.create(
            name="Web Development",
            description="Build websites",
            skills="Python, Django"
        )
        self.assertEqual(str(service), "Web Development")

    def test_service_page_str(self):
        page = Service_page.objects.create(
            titel="Our Services",
            page_description="Service description"
        )
        self.assertEqual(str(page), "Our Services")

    def test_service_request_str(self):
        user = User.objects.create_user(username="tester", password="password123")
        service_request = ServiceRequest.objects.create(
            user=user,
            title="Need Web App",
            description="Build me a web app"
        )
        self.assertIn("Need Web App", str(service_request))
        self.assertIn("tester", str(service_request))


class ServicesViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="john", password="password123")
        self.service = Service.objects.create(
            name="Graphic Design",
            description="Design services",
            skills="Photoshop, Illustrator"
        )
        self.service_page = Service_page.objects.create(titel="Service Page")
        self.profile = UserProfile.objects.create(user=self.user, skills="Photoshop")

    def test_services_view(self):
        response = self.client.get(reverse("services"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "services/services.html")

    def test_all_services_view(self):
        response = self.client.get(reverse("all_services"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Graphic Design")

    def test_service_candidates_view(self):
        response = self.client.get(reverse("service_candidates", args=[self.service.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "services/candidates.html")
        self.assertContains(response, "Graphic Design")

    def test_candidate_profile_view(self):
        response = self.client.get(
            reverse("candidate_profile", args=[self.profile.id]) + f"?service_id={self.service.id}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "services/candidate_profile.html")


    def test_request_service_post(self):
        self.client.login(username="john", password="password123")
        response = self.client.post(reverse("request_service"), {
            "title": "Need Design",
            "description": "Logo and posters"
        })
        self.assertRedirects(response, reverse("service_request_success"))
        self.assertTrue(ServiceRequest.objects.filter(title="Need Design").exists())

    def test_request_service_get(self):
        self.client.login(username="john", password="password123")
        response = self.client.get(reverse("request_service"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "services/request_service.html")

    def test_service_request_success_view(self):
        response = self.client.get(reverse("service_request_success"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "services/request_success.html")
