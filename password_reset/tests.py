from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()

class PasswordResetTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )

    def test_password_reset_get_request(self):
        response = self.client.get(reverse('password_reset'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'password_reset/password_reset_form.html')

    def test_password_reset_post_valid_email(self):
        response = self.client.post(
            reverse('password_reset'),
            {'email_or_phone': 'test@example.com'},
            HTTP_HOST='testserver'  # add this
        )

        self.assertRedirects(response, reverse('password_reset_done'))

    def test_password_reset_post_invalid_email(self):
        response = self.client.post(reverse('password_reset'), {'email_or_phone': 'invalid@example.com'})

        form = response.context['form']
        self.assertIn('email_or_phone', form.errors)
        self.assertEqual(form.errors['email_or_phone'], ['No user is associated with this email or phone number.'])


    def test_password_reset_done_view(self):
        response = self.client.get(reverse('password_reset_done'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'password_reset/password_reset_done.html')

    def test_password_reset_confirm_view(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)

        response = self.client.get(
            reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token}),
            follow=True  # Add follow=True to get actual 200 status
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'password_reset/password_reset_confirm.html')

    def test_password_reset_complete_view(self):
        response = self.client.get(reverse('password_reset_complete'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'password_reset/password_reset_complete.html')

