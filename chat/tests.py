from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from chat.models import ChatSession, Message
from progress_tracker.models import ProjectDetails

User = get_user_model()

class ChatAppTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1",
            password="pass123",
            phone="1111111111",          # unique phone
            email="user1@example.com"    # unique email
        )
        self.user2 = User.objects.create_user(
            username="user2",
            password="pass123",
            phone="2222222222",          # unique phone
            email="user2@example.com"    # unique email
        )
        self.client.login(username="user1", password="pass123")

    def test_inbox_view(self):
        url = reverse('messages')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat/messages.html')

    def test_start_chat_creates_session(self):
        url = reverse('start_chat', args=[self.user2.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ChatSession.objects.count(), 1)

    def test_chat_session_view(self):
        chat_session = ChatSession.objects.create()
        chat_session.participants.add(self.user1, self.user2)
        url = reverse('chat_session', args=[chat_session.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat/chat_session.html')

    def test_send_message(self):
        chat_session = ChatSession.objects.create()
        chat_session.participants.add(self.user1, self.user2)
        url = reverse('chat_session', args=[chat_session.id])
        data = {'content': 'Hello Test!'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Message.objects.filter(content='Hello Test!').exists())

    def test_assign_project_view(self):
        url = reverse('assign_project', args=[self.user2.id])
        data = {
            'project_name': 'Test Project',
            'description': 'This is a test project'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ProjectDetails.objects.filter(
            candidate=self.user2,
            recruiter=self.user1,
            project_name='Test Project'
        ).exists())



