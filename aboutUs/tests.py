from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from aboutUs.models import AboutUsContent, TeamMember
from profiles.models import UserProfile

User = get_user_model()

class AboutUsViewTests(TestCase):

    def test_about_us_view_with_normal_user(self):
        # Normal user create
        user = User.objects.create_user(
            username="normaluser",
            password="pass"
        )
        # Profile image add
        profile_img = SimpleUploadedFile("profile.jpg", b"file_content", content_type="image/jpeg")
        UserProfile.objects.create(user=user, profile_image=profile_img)

        # Login
        self.client.login(username="normaluser", password="pass")

        # About Us content
        AboutUsContent.objects.create(title="Normal User About Us")

        # Request
        url = reverse("aboutUs_view")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["about_us_content"].title, "Normal User About Us")
        self.assertIsNotNone(response.context["profile_image_url"])

    def test_about_us_view_with_superuser(self):
        # Superuser create
        admin_user = User.objects.create_superuser(
            username="adminuser",
            password="pass"
        )
        # Profile image add
        profile_img = SimpleUploadedFile("admin_profile.jpg", b"file_content", content_type="image/jpeg")
        UserProfile.objects.create(user=admin_user, profile_image=profile_img)

        # Login
        self.client.login(username="adminuser", password="pass")

        # About Us content
        AboutUsContent.objects.create(title="Admin About Us")

        # Request
        url = reverse("aboutUs_view")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["about_us_content"].title, "Admin About Us")
        self.assertIsNotNone(response.context["profile_image_url"])



    def test_about_us_view_guest_user(self):
        # About Us content create (optional, dekhne ke liye ki guest ko bhi dikh raha hai)
        about_us = AboutUsContent.objects.create(title="Guest View Title")

        # Guest user (no login)
        url = reverse("aboutUs_view")
        response = self.client.get(url)

        # Status check
        self.assertEqual(response.status_code, 200)

        # Template check
        self.assertTemplateUsed(response, "aboutUs/aboutUs.html")

        # Context check
        self.assertEqual(response.context["about_us_content"], about_us)
        self.assertIsNone(response.context["profile_image_url"])
