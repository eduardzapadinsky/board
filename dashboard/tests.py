from unittest.mock import patch

from django.test import Client
from django.test import TestCase
from django.urls import reverse

from dashboard.forms import CardForm
from dashboard.models import Card
from user.models import UserModel


# class CardListViewTest(TestCase):
#
#     def setUp(self):
#         self.user = UserModel.objects.create_user(username="admin1", password="Admin123")
#         self.client = Client()
#         self.client.login(username="admin1", password="Admin123")
#         self.card1 = Card.objects.create(description='Card 1', creator=self.user)
#         self.card2 = Card.objects.create(description='Card 2', creator=self.user)
#         self.card3 = Card.objects.create(description='Card 3', creator=self.user)
#         self.url = reverse('dashboard:board')
#
#     def test_view_url_exists(self):
#         response = self.client.get("/board/")
#         self.assertEqual(response.status_code, 200)
#
#     def test_view_lists_all_cards(self):
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, self.card1.description)
#         self.assertContains(response, self.card2.description)
#         self.assertContains(response, self.card3.description)
#
#
# class CardCreateViewTest(TestCase):
#     def setUp(self):
#         self.url = reverse('dashboard:card-create')
#         self.client = Client()
#         self.user1 = UserModel.objects.create_user(
#             username='testuser',
#             password='testpass'
#         )
#         self.user2 = UserModel.objects.create_user(
#             username='testuser2',
#             password='testpass2'
#         )
#         self.user_admin = UserModel.objects.create_superuser(
#             username='adminuser',
#             password='testpass',
#         )
#
#     def test_get_card_create_view(self):
#         self.client.login(username='testuser', password='testpass')
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'dashboard/card_form.html')
#         self.assertIsInstance(response.context['form'], CardForm)
#
#     def test_post_valid_executor_none(self):
#         self.client.login(username='testuser', password='testpass')
#         data = {
#             'description': 'Test card'
#         }
#         response = self.client.post(self.url, data)
#         self.assertEqual(response.status_code, 302)
#         self.assertRedirects(response, reverse('dashboard:board'))
#         self.assertTrue(Card.objects.filter(
#             creator=self.user1, description='Test card', executor=None
#         ).exists())
#
#     def test_post_valid_executor_user(self):
#         self.client.login(username='testuser', password='testpass')
#         data = {
#             'description': '',
#             "executor": self.user1
#         }
#         response = self.client.post(self.url, data)
#         self.assertEqual(response.status_code, 302)
#         self.assertFalse(Card.objects.filter(
#             creator=self.user1, description='', executor=self.user1
#         ).exists())
#
#     def test_post_invalid_executor_user(self):
#         self.client.login(username='testuser', password='testpass')
#         data = {
#             'description': 'Test card',
#             "executor": self.user2
#         }
#         response = self.client.post(self.url, data)
#         self.assertEqual(response.status_code, 302)
#         self.assertFalse(Card.objects.filter(
#             creator=self.user1, description='Test card', executor=self.user2
#         ).exists())
#
#     def test_post_valid_superuser(self):
#         self.client.login(username='adminuser', password='testpass')
#         data = {
#             'description': 'Test card',
#             "executor": self.user2
#         }
#         response = self.client.post(self.url, data)
#         self.assertEqual(response.status_code, 403)
#
#
# class CardUpdateViewTest(TestCase):
#
#     def setUp(self):
#         self.client = Client()
#         self.user = UserModel.objects.create_user(username='testuser', password='testpass')
#         self.client.force_login(self.user)
#         self.card = Card.objects.create(description='Test card', creator=self.user)
#
#     def test_form_valid_without_executor(self):
#         self.client.login(username='testuser', password='testpass')
#         url = reverse('dashboard:card-update', kwargs={'pk': self.card.pk})
#         data = {'description': 'Updated Test Card'}
#         with patch('dashboard.views.CardUpdateView.get_success_url', return_value='/dashboard/board/'):
#             response = self.client.post(url, data)
#         self.assertEqual(response.status_code, 302)
#         self.assertEqual(response.url, '/dashboard/board/')
#         self.card.refresh_from_db()
#         self.assertEqual(self.card.description, 'Updated Test Card')
#         self.client.logout()
#
#     def test_form_valid_with_executor(self):
#         self.client.login(username='testuser', password='testpass', executor=self.user)
#         url = reverse('dashboard:card-update', kwargs={'pk': self.card.pk})
#         data = {'description': 'Updated Test Card', "executor": ""}
#         with patch('dashboard.views.CardUpdateView.get_success_url', return_value='/dashboard/board/'):
#             response = self.client.post(url, data)
#         self.assertEqual(response.status_code, 302)
#         self.assertEqual(response.url, '/dashboard/board/')
#         self.card.refresh_from_db()
#         self.assertEqual(self.card.description, 'Updated Test Card')
#         self.assertEqual(self.card.executor, None)
#         self.client.logout()
#

# class CardUpdateViewSuperuserTest(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.superuser = UserModel.objects.create_superuser(username='testsuperuser', password='testpass')
#         self.user = UserModel.objects.create_user(username='testuser', password='testpass')
#         self.client.force_login(self.user)
#         self.card = Card.objects.create(description='Test card', creator=self.user)
#         self.client.logout()
#
#     def test_form_valid(self):
#         self.client.force_login(self.superuser)
#         url = reverse('dashboard:card-full-update', kwargs={'pk': self.card.pk})
#         data = {'description': 'Updated Test Card'}
#         with patch('dashboard.views.CardUpdateView.get_success_url', return_value='/dashboard/board/'):
#             response = self.client.post(url, data)
#         self.assertEqual(response.status_code, 302)
#         self.assertEqual(response.url, '/board/')
#         self.card.refresh_from_db()
#         self.assertEqual(self.card.description, 'Updated Test Card')
#         self.client.logout()
#
#     def test_form_invalid(self):
#         self.client.force_login(self.user)
#         url = reverse('dashboard:card-full-update', kwargs={'pk': self.card.pk})
#         data = {'description': 'Updated Test Card'}
#         with patch('dashboard.views.CardUpdateView.get_success_url', return_value='/dashboard/board/'):
#             response = self.client.post(url, data)
#         self.assertEqual(response.status_code, 403)
#         self.card.refresh_from_db()
#         self.assertNotEqual(self.card.description, 'Updated Test Card')
#         self.client.logout()

class CardDeleteViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.superuser = UserModel.objects.create_superuser(username='testsuperuser', password='testpass')
        self.user = UserModel.objects.create_user(username='testuser', password='testpass')
        self.client.force_login(self.user)
        self.card = Card.objects.create(description='Test card', creator=self.user)
        self.client.logout()

    def test_delete_card_valid(self):
        self.client.force_login(self.superuser)
        response = self.client.get(reverse('dashboard:card-delete', args=[self.card.pk]))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('dashboard:card-delete', args=[self.card.pk]), data={'confirm': True})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard:board'))

        self.assertFalse(Card.objects.filter(pk=self.card.pk).exists())

    def test_delete_card_invalid(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('dashboard:card-delete', args=[self.card.pk]))
        self.assertEqual(response.status_code, 403)
