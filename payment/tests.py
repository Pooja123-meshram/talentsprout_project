from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from decimal import Decimal

from .models import Subscription, Payment, Profile
from signUp.models import CustomUser
from profiles.models import UserProfile

User = get_user_model()


class PaymentViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Create test recruiter (logged-in user)
        self.recruiter = CustomUser.objects.create_user(
            username='recruiter1',
            password='testpass123',
            email='recruiter@example.com',
            phone='9999999991',
            role='recruiter'
        )

        # Create test candidate
        self.candidate = CustomUser.objects.create_user(
            username='candidate1',
            password='testpass123',
            email='candidate@example.com',
            phone='9999999992',  
            role='candidate'
        )

        # Create subscription
        self.subscription = Subscription.objects.create(
            name="Basic Plan",
            price=Decimal('100.00'),
            features="Feature1,Feature2"
        )

        # Create recruiter profile
        self.profile = Profile.objects.create(
            user=self.recruiter,
            preferred_candidate_username=self.candidate.username
        )

        # Create recruiter UserProfile for image
        self.user_profile = UserProfile.objects.create(
            user=self.recruiter
        )

    @patch('payment.views.razorpay_client')
    def test_payment_page_view(self, mock_razorpay_client):
        """Test that payment_page renders correctly with mocked Razorpay order"""
        mock_razorpay_client.order.create.return_value = {'id': 'order_123'}

        self.client.login(username='recruiter1', password='testpass123')
        url = reverse('payment_page', args=[self.candidate.id, self.subscription.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payment/payment_page.html')
        self.assertIn('razorpay_order_id', response.context)
        self.assertEqual(response.context['razorpay_order_id'], 'order_123')

    @patch('payment.views.razorpay_client')
    def test_custom_payment_post(self, mock_razorpay_client):
        """Test custom_payment with POST request and mocked Razorpay"""
        mock_razorpay_client.order.create.return_value = {'id': 'order_456'}

        self.client.login(username='recruiter1', password='testpass123')
        url = reverse('custom_payment', args=[self.candidate.id])
        response = self.client.post(url, {
            'custom_amount': '500',
            'description': 'Special Payment'
        })

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payment/custom_payment.html')
        self.assertEqual(response.context['razorpay_order_id'], 'order_456')

    def test_subscription_list_view(self):
        """Test subscription_list renders and contains subscriptions"""
        self.client.login(username='recruiter1', password='testpass123')
        url = reverse('subscription_list', args=[self.candidate.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payment/subscription_list.html')
        self.assertTrue(len(response.context['subscriptions']) > 0)

    def test_payment_failed_view(self):
        """Test payment_failed view renders with error context"""
        self.client.login(username='recruiter1', password='testpass123')
        url = reverse('payment_failed') + '?error_code=TEST_ERR&error_description=Something%20went%20wrong'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payment/payment_failed.html')
        self.assertEqual(response.context['error_code'], 'TEST_ERR')

    def test_payment_successful_missing_payment_id(self):
        """Test payment_successful without payment_id returns failure template"""
        self.client.login(username='recruiter1', password='testpass123')
        url = reverse('payment_successful')
        response = self.client.get(url)

        self.assertTemplateUsed(response, 'payment/payment_failed.html')
        self.assertEqual(response.context['error_code'], 'MISSING_PAYMENT_ID')

    def test_edit_billing_info_get(self):
        """Test edit_billing_info GET request renders form"""
        self.client.login(username='recruiter1', password='testpass123')
        url = reverse('edit_billing_info', args=[self.candidate.id, self.subscription.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payment/edit_billing_info.html')

    def test_edit_billing_info_post_redirects(self):
        """Test edit_billing_info POST request updates profile and redirects"""
        self.client.login(username='recruiter1', password='testpass123')
        url = reverse('edit_billing_info', args=[self.candidate.id, self.subscription.id])
        response = self.client.post(url, {
            'full_name': 'Recruiter Test',
            'preferred_candidate_username': self.candidate.username
        })
        self.assertEqual(response.status_code, 302)  # Redirect after POST


