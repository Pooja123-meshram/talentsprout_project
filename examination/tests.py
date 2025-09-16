from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from .models import Skill, Question, Test, Answer, ExamRule
from profiles.models import UserProfile

User = get_user_model()


class ExamSystemTests(TestCase):

    def setUp(self):
        # Create user and profile
        self.user = User.objects.create_user(username='testuser', password='password')
        self.profile = UserProfile.objects.create(user=self.user)
        self.client = Client()
        self.client.login(username='testuser', password='password')

        # Create skill
        self.skill = Skill.objects.create(name='Python', description='Python skill test')

        # Create questions
        self.q1 = Question.objects.create(skill=self.skill, type='MCQ', text='Q1', correct_answer='A', is_second_attempt=False)
        self.q2 = Question.objects.create(skill=self.skill, type='MCQ', text='Q2', correct_answer='B', is_second_attempt=False)
        self.q3 = Question.objects.create(skill=self.skill, type='MCQ', text='Q3', correct_answer='C', is_second_attempt=True)

        # Create rules
        self.rule = ExamRule.objects.create(title='Rule 1', description='Rule description')

    def test_rules_page_loads_and_post(self):
        url = reverse('rules_and_regulations')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Rule 1')

        response_post = self.client.post(url)
        self.assertRedirects(response_post, reverse('choose_skill'))
        self.assertTrue(self.client.session['accepted_rules'])

    def test_choose_skill_page(self):
        url = reverse('choose_skill')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.skill.name)

    def test_start_test_first_attempt_fetches_questions(self):
        url = reverse('start_test', args=[self.skill.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect to take_test

        test = Test.objects.get(user=self.user, skill=self.skill, completed=False)
        questions = test.questions.all()
        self.assertEqual(list(questions), [self.q1, self.q2])

    def test_start_test_second_attempt_fetches_second_attempt_questions(self):
        url = reverse('start_test', args=[self.skill.id]) + '?second_attempt=true'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        test = Test.objects.get(user=self.user, skill=self.skill, completed=False)
        questions = test.questions.all()
        self.assertEqual(list(questions), [self.q3])

    def test_take_test_post_and_complete(self):
        # Start a test
        test = Test.objects.create(user=self.user, skill=self.skill, completed=False)
        test.questions.set([self.q1, self.q2])

        url = reverse('take_test', args=[test.id])
        data = {
            f'question_{self.q1.id}': 'A',
            f'question_{self.q2.id}': 'B'
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('test_completed', args=[test.id]))

        # Reload test
        test.refresh_from_db()
        self.assertTrue(test.completed)
        self.assertEqual(test.answers.count(), 2)
        self.assertTrue(all(answer.is_correct for answer in test.answers.all()))

    def test_test_completed_page(self):
        test = Test.objects.create(user=self.user, skill=self.skill, completed=True)
        url = reverse('test_completed', args=[test.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'examination/test_completed.html')


    def test_cannot_retake_before_wait_period(self):
        # Create a completed test
        test = Test.objects.create(user=self.user, skill=self.skill, completed=True, completed_date=timezone.now())
        test.score = 80
        test.save()

        url = reverse('start_test', args=[self.skill.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'examination/cannot_retake_test.html')
        self.assertIn('You passed the exam', response.content.decode())

