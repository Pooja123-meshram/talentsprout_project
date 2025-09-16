from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch
from signUp.models import CustomUser
from profiles.models import UserProfile
from services.models import Service, Service_page
from admin_customization.models import HeroSection, WorkStep, ContactInfo, WhyChooseUs

User = get_user_model()


class LayoutAndHomeViewTests(TestCase):
    def setUp(self):
        # Create an authenticated user
        self.user = CustomUser.objects.create_user(
            username="testuser",
            password="pass1234",
            role=CustomUser.CANDIDATE,
            first_name="John",
            last_name="Doe"
        )

        # Create user profile (with and without image for tests)
        self.profile_with_image = UserProfile.objects.create(
            user=self.user,
            profile_image=None,  # can later set a mock image in tests
            level=5,
            career_objective="Become a top developer"
        )

        # Create some dummy data for home_view
        for i in range(8):  # more than 6 to test pagination
            Service.objects.create(name=f"Service {i+1}")

        Service_page.objects.create(titel="Test Service Page")
        HeroSection.objects.create(heading="Hero", description="Welcome")
        WorkStep.objects.create(title="Step 1", description="Do something")
        ContactInfo.objects.create(address="123 Street", phone="123456789")
        WhyChooseUs.objects.create(heading="Why Us", sub_heading="Because we're great")





    def test_home_view_anonymous_user(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/Index.html')
        self.assertIsNone(response.context['profile_image_url'])

    def test_home_view_authenticated_user_with_profile(self):
        self.client.login(username="testuser", password="pass1234")
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('users', response.context)
        self.assertIn('profile_image_url', response.context)
        self.assertTrue(len(response.context['users']) <= 5)  # top 5 candidates

    def test_home_view_pagination(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        page_obj = response.context['page_obj']
        self.assertEqual(page_obj.paginator.num_pages, 2)  # because 8 services, 6 per page

