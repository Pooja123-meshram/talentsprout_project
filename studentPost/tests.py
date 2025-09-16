from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import Group
from studentPost.models import BlogPost, CandidatePreference, BlogImage
from profiles.models import UserProfile
from examination.models import Test
from django.utils import timezone
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile


User = get_user_model()


def generate_test_image():
    file = BytesIO()
    image = Image.new("RGB", (100, 100), "blue")  # 100x100 blue square
    image.save(file, "JPEG")
    file.seek(0)
    return SimpleUploadedFile("test.jpg", file.read(), content_type="image/jpeg")

class StudentPostViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        # create candidate group if required
        Group.objects.get_or_create(name="Candidate")

        # Create user
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@test.com",
            password="testpassword123",
            email_verified=True
        )
        self.client.login(username="testuser", password="testpassword123")

        # Create profile
        self.profile = UserProfile.objects.create(user=self.user)

        # Create a blog post
        self.post = BlogPost.objects.create(
            user=self.user,
            title="Test Post",
            content="This is a test post",
            status="published",
            publication_date=timezone.now()
        )


        self.image = BlogImage.objects.create(
            blog_post=self.post,
            image=SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        )




    def test_student_post_view(self):
        response = self.client.get(reverse("studentpost"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "studentPost/studentPost.html")
        self.assertContains(response, "Test Post")

    def test_post_detail_view(self):
        response = self.client.get(reverse("postdetail", args=[self.post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "studentPost/postdetailes.html")
        self.assertContains(response, "Test Post")

    def test_all_posts_view(self):
        response = self.client.get(reverse("all_posts"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "studentPost/all_posts.html")
        self.assertContains(response, "Test Post")

    def test_load_more_posts_api(self):
        response = self.client.get(reverse("load_more_posts"), {"page": 1})
        self.assertEqual(response.status_code, 200)
        self.assertIn("posts", response.json())
        self.assertTrue(any(post["title"] == "Test Post" for post in response.json()["posts"]))

    def test_create_blog_post_requires_exam_pass(self):
        # Patch Test.fetch_latest_score to simulate exam fail
        def fake_score_fail(user): return 50
        Test.fetch_latest_score = fake_score_fail

        response = self.client.get(reverse("create_blog_post"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "studentPost/access_denied.html")





    def test_create_blog_post_success(self):
        # Patch Test.fetch_latest_score to simulate exam pass
        def fake_score_pass(user): return 90
        Test.fetch_latest_score = fake_score_pass

        image = generate_test_image() 

        response = self.client.post(
            reverse("create_blog_post"),
            {
                "title": "New Blog Post",
                "author": "Test Author",
                "publication_date": "2025-08-20T10:00",  # ✅ Correct format
                "content": "This is a valid blog post",
                "status": "published",

                "service_title": "Software Engineer",
                "description": "Backend developer role",
                "delivery_time": "2 weeks",
                "revisions": "3",
                "price": "5000.00",

                "image": image,
            },
            format="multipart"
        )

        if response.status_code != 302:
            print("Blog post form errors:", response.context["blog_post_form"].errors)
            print("Candidate preference form errors:", response.context["candidate_preference_form"].errors)
            print("Blog image form errors:", response.context["blog_image_form"].errors)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(BlogPost.objects.filter(title="New Blog Post").exists())
        self.assertTrue(CandidatePreference.objects.filter(service_title="Software Engineer").exists())
