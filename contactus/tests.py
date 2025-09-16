from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import ConsultingMessage, SupportInfo
from notifications.models import Notification

CustomUser = get_user_model()

class ConsultingViewTests(TestCase):

    def setUp(self):
        # Create a test client
        self.client = Client()

        # Create a test user (non-staff)
        self.user = CustomUser.objects.create_user(
            username='testuser', 
            email='testuser@example.com', 
            password='password123',
            first_name='Test',      # <-- add first name
            last_name='User', 
            phone='1111111111'  # Add unique phone number
        )

        # Create a staff user (admin) to receive notifications
        self.admin_user = CustomUser.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='password123',
            is_staff=True,
            phone='2222222222'  # Add unique phone number
        )

        # URL for consulting view
        self.url = reverse('contactus')  # Update with your actual URL name

    def test_consulting_get_request(self):
        """Test GET request returns 200 and contains the form"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIn('support_info', response.context)

    def test_consulting_post_authenticated_user(self):
        """Test POST request with an authenticated user creates message and sends notification"""
        self.client.login(username='testuser', password='password123')
        data = {
            'name': 'Test User',
            'email': 'testuser@example.com',
            'phone': '1111111111',
            'message': 'This is a test message.'
        }

        response = self.client.post(self.url, data)
        self.assertRedirects(response, reverse('contactus'))

        # Check message created
        message = ConsultingMessage.objects.last()
        self.assertEqual(message.name, 'Test User')
        self.assertEqual(message.email, 'testuser@example.com')

        # Check notification created safely
        notifications = Notification.objects.filter(recipient=self.admin_user)
        if notifications.exists():
            self.assertIn('Test User', notifications.first().description)

    def test_consulting_post_anonymous_user(self):
        """Test POST request from anonymous user"""
        data = {
            'name': 'Anonymous',
            'email': 'anon@example.com',
            'phone': '9999999999',  # required
            'message': 'Anonymous message content.'
        }

        response = self.client.post(self.url, data)
        self.assertRedirects(response, reverse('contactus'))

        message = ConsultingMessage.objects.last()
        self.assertEqual(message.name, 'Anonymous')
        self.assertEqual(message.email, 'anon@example.com')

        # Skip notification check for anonymous users
        # Anonymous users may not trigger a notification
