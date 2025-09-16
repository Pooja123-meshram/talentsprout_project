from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.messages import get_messages

User = get_user_model()

class AuthViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create groups
        for group_name in ['Candidate', 'Recruiter', 'Admin']:
            Group.objects.create(name=group_name)

        # Create a verified candidate user
        self.candidate_user = User.objects.create_user(
            username='candidate1',
            email='candidate1@test.com',
            password='TestPass@123',   # correct password
            email_verified=True,
            first_name='Alice',
            last_name='Smith',
            phone='9123456780',
        )
        candidate_group = Group.objects.get(name='Candidate')
        self.candidate_user.groups.add(candidate_group)
        self.candidate_user.role = User.CANDIDATE
        self.candidate_user.save()

    def test_signup_page_loads(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'signUp/chooseSignUp.html')

    def test_candidate_signup(self):
        response = self.client.post(reverse('candidateSignUp'), {
            'username': 'newcandidate',
            'email': 'newcandidate@test.com',
            'first_name': 'Bob',
            'last_name': 'Brown',
            'phone': '9234567890',
            'password1': 'TestPass@123',
            'password2': 'TestPass@123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newcandidate').exists())

    def test_candidate_login_success(self):
        response = self.client.post(reverse('candidatelogin'), {
            'username': 'candidate1',
            'password': 'TestPass@123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.candidate_user.pk)

    def test_candidate_login_fail_unverified_email(self):
        unverified_user = User.objects.create_user(
            username='unverified',
            email='unverified@test.com',
            password='TestPass@123',
            email_verified=False,
            first_name='John',
            last_name='Doe',
            phone='9234567891',
        )
        response = self.client.post(reverse('candidatelogin'), {
            'username': 'unverified',
            'password': 'TestPass@123'
        })
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Email is not verified" in str(m) for m in messages))

    def test_logout(self):
        self.client.login(username='candidate1', password='TestPass@123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('_auth_user_id', self.client.session)
