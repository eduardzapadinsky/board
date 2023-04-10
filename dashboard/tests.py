from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.test import Client
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from dashboard.forms import CardForm
from dashboard.models import Card
from dashboard.serializers import CardSerializer
from user.models import UserModel


class CardListViewTest(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(username="admin1", password="Admin123")
        self.client = Client()
        self.client.login(username="admin1", password="Admin123")
        self.card1 = Card.objects.create(description='Card 1', creator=self.user)
        self.card2 = Card.objects.create(description='Card 2', creator=self.user)
        self.card3 = Card.objects.create(description='Card 3', creator=self.user)
        self.url = reverse('dashboard:board')

    def test_view_url_exists(self):
        response = self.client.get("/board/")
        self.assertEqual(response.status_code, 200)

    def test_view_lists_all_cards(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.card1.description)
        self.assertContains(response, self.card2.description)
        self.assertContains(response, self.card3.description)


class CardCreateViewTest(TestCase):
    def setUp(self):
        self.url = reverse('dashboard:card-create')
        self.client = Client()
        self.user1 = UserModel.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.user2 = UserModel.objects.create_user(
            username='testuser2',
            password='testpass2'
        )
        self.user_admin = UserModel.objects.create_superuser(
            username='adminuser',
            password='testpass',
        )

    def test_get_card_create_view(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/card_form.html')
        self.assertIsInstance(response.context['form'], CardForm)

    def test_post_valid_executor_none(self):
        self.client.login(username='testuser', password='testpass')
        data = {
            'description': 'Test card'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard:board'))
        self.assertTrue(Card.objects.filter(
            creator=self.user1, description='Test card', executor=None
        ).exists())

    def test_post_valid_executor_user(self):
        self.client.login(username='testuser', password='testpass')
        data = {
            'description': '',
            "executor": self.user1
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Card.objects.filter(
            creator=self.user1, description='', executor=self.user1
        ).exists())

    def test_post_invalid_executor_user(self):
        self.client.login(username='testuser', password='testpass')
        data = {
            'description': 'Test card',
            "executor": self.user2
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Card.objects.filter(
            creator=self.user1, description='Test card', executor=self.user2
        ).exists())

    def test_post_valid_superuser(self):
        self.client.login(username='adminuser', password='testpass')
        data = {
            'description': 'Test card',
            "executor": self.user2
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 403)


class CardUpdateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserModel.objects.create_user(username='testuser', password='testpass')
        self.client.force_login(self.user)
        self.card = Card.objects.create(description='Test card', creator=self.user)

    def test_form_valid_without_executor(self):
        self.client.login(username='testuser', password='testpass')
        url = reverse('dashboard:card-update', kwargs={'pk': self.card.pk})
        data = {'description': 'Updated Test Card'}
        with patch('dashboard.views.CardUpdateView.get_success_url', return_value='/dashboard/board/'):
            response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/dashboard/board/')
        self.card.refresh_from_db()
        self.assertEqual(self.card.description, 'Updated Test Card')
        self.client.logout()

    def test_form_valid_with_executor(self):
        self.client.login(username='testuser', password='testpass', executor=self.user)
        url = reverse('dashboard:card-update', kwargs={'pk': self.card.pk})
        data = {'description': 'Updated Test Card', "executor": ""}
        with patch('dashboard.views.CardUpdateView.get_success_url', return_value='/dashboard/board/'):
            response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/dashboard/board/')
        self.card.refresh_from_db()
        self.assertEqual(self.card.description, 'Updated Test Card')
        self.assertEqual(self.card.executor, None)
        self.client.logout()


class CardUpdateViewSuperuserTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.superuser = UserModel.objects.create_superuser(username='testsuperuser', password='testpass')
        self.user = UserModel.objects.create_user(username='testuser', password='testpass')
        self.client.force_login(self.user)
        self.card = Card.objects.create(description='Test card', creator=self.user)
        self.client.logout()

    def test_form_valid(self):
        self.client.force_login(self.superuser)
        url = reverse('dashboard:card-full-update', kwargs={'pk': self.card.pk})
        data = {'description': 'Updated Test Card'}
        with patch('dashboard.views.CardUpdateView.get_success_url', return_value='/dashboard/board/'):
            response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/board/')
        self.card.refresh_from_db()
        self.assertEqual(self.card.description, 'Updated Test Card')
        self.client.logout()

    def test_form_invalid(self):
        self.client.force_login(self.user)
        url = reverse('dashboard:card-full-update', kwargs={'pk': self.card.pk})
        data = {'description': 'Updated Test Card'}
        with patch('dashboard.views.CardUpdateView.get_success_url', return_value='/dashboard/board/'):
            response = self.client.post(url, data)
        self.assertEqual(response.status_code, 403)
        self.card.refresh_from_db()
        self.assertNotEqual(self.card.description, 'Updated Test Card')
        self.client.logout()


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


class CardMoveLeftTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.superuser = UserModel.objects.create_superuser(username='testsuperuser', password='testpass')
        self.user = UserModel.objects.create_user(username='testuser', password='testpass')
        self.client.force_login(self.user)
        self.card = Card.objects.create(description='Test card', creator=self.user, status="In_progress")

    def test_form_with_executor_valid(self):
        self.card.executor = self.user
        self.card.save()
        self.url = reverse('dashboard:card-move-left', kwargs={'pk': self.card.pk})
        response = self.client.patch(self.url)
        self.card.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.card.status, 'New')

    def test_form_with_executor_invalid(self):
        self.card.executor = self.user
        self.card.status = "Done"
        self.card.save()
        self.url = reverse('dashboard:card-move-left', kwargs={'pk': self.card.pk})
        response = self.client.patch(self.url)
        self.card.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertNotEqual(self.card.status, 'Ready')

    def test_form_without_executor_valid(self):
        self.url = reverse('dashboard:card-move-left', kwargs={'pk': self.card.pk})
        response = self.client.patch(self.url)
        self.card.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertNotEqual(self.card.status, 'New')

    def test_form_with_executor_superuser_valid(self):
        self.client.logout()
        self.client.force_login(self.superuser)
        self.card.status = "Done"
        self.card.save()
        self.url = reverse('dashboard:card-move-left', kwargs={'pk': self.card.pk})
        response = self.client.patch(self.url)
        self.card.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.card.status, 'Ready')

    def test_form_with_executor_superuser_invalid(self):
        self.client.logout()
        self.client.force_login(self.superuser)
        self.card.status = "Ready"
        self.card.save()
        self.url = reverse('dashboard:card-move-left', kwargs={'pk': self.card.pk})
        response = self.client.patch(self.url)
        self.card.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertNotEqual(self.card.status, 'In_QA')


class CardMoveRightTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.superuser = UserModel.objects.create_superuser(username='testsuperuser', password='testpass')
        self.user = UserModel.objects.create_user(username='testuser', password='testpass')
        self.client.force_login(self.user)
        self.card = Card.objects.create(description='Test card', creator=self.user)

    def test_form_with_executor_valid(self):
        self.card.executor = self.user
        self.card.save()
        self.url = reverse('dashboard:card-move-right', kwargs={'pk': self.card.pk})
        response = self.client.patch(self.url)
        self.card.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.card.status, 'In_progress')

    def test_form_with_executor_invalid(self):
        self.card.executor = self.user
        self.card.status = "Ready"
        self.card.save()
        self.url = reverse('dashboard:card-move-right', kwargs={'pk': self.card.pk})
        response = self.client.patch(self.url)
        self.card.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertNotEqual(self.card.status, 'Done')

    def test_form_without_executor_valid(self):
        self.url = reverse('dashboard:card-move-right', kwargs={'pk': self.card.pk})
        response = self.client.patch(self.url)
        self.card.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertNotEqual(self.card.status, 'In_progress')

    def test_form_with_executor_superuser_valid(self):
        self.client.logout()
        self.client.force_login(self.superuser)
        self.card.status = "Ready"
        self.card.save()
        self.url = reverse('dashboard:card-move-right', kwargs={'pk': self.card.pk})
        response = self.client.patch(self.url)
        self.card.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.card.status, 'Done')

    def test_form_with_executor_superuser_invalid(self):
        self.client.logout()
        self.client.force_login(self.superuser)
        self.card.status = "In_QA"
        self.card.save()
        self.url = reverse('dashboard:card-move-right', kwargs={'pk': self.card.pk})
        response = self.client.patch(self.url)
        self.card.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertNotEqual(self.card.status, 'Ready')


class CardDetailViewAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserModel.objects.create(username="testuser", password='testpass')
        self.client.force_authenticate(user=self.user)
        self.card = Card.objects.create(description="Test Card",
                                        status=Card.IN_PROGRES,
                                        creator=self.user,
                                        executor=self.user)

    def test_get_card_detail(self):
        url = reverse("dashboard:card-detail", kwargs={"status": "in_progress", "pk": self.card.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, CardSerializer(self.card).data)


class CardListViewAPITestCase(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser', password='password'
        )
        self.client.force_authenticate(user=self.user)

    def test_card_creation(self):
        url = reverse('card-list')
        data = {'description': 'Test card'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Card.objects.count(), 1)
        self.assertEqual(Card.objects.get().creator, self.user)
