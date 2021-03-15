from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Game, Tournament
from blazing.serializers import TournamentSerializer

TOURNAMENTS_URL = reverse('blazing:tournament-list')


class PublicTournamentTestCase(TestCase):
    """Test publicly available tournament API"""

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_tournaments(self):
        """Test retrieve tournaments"""
        Tournament.objects.create(name="New Tournament")
        Tournament.objects.create(name="New Tournament 2")

        res = self.client.get(TOURNAMENTS_URL)
        tournaments = Tournament.objects.all()
        serializer = TournamentSerializer(tournaments, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_required_auth_to_create(self):
        """Test if login is required to create"""
        payload = { 'name': 'Tournament' }
        res = self.client.post(TOURNAMENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTournamentTestCase(TestCase):
    """Test non superuser authorized user tournament api"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@londonappdev.com',
            'password'
        )
        self.client.force_authenticate(self.user)

    def test_non_superuser_create_tournament_(self):
        """Test create tournament as non superuser"""
        payload = { 'name': 'Tournament' }
        res = self.client.post(TOURNAMENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class PrivateSuperUserTournamentTestCase(TestCase):
    """Test superuser authorized user tournament api"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            'test@londonappdev.com',
            'password'
        )
        self.client.force_authenticate(self.user)

    def test_create_tournament(self):
        """Test create tournament as superuser"""
        payload = { 'name': 'Tournament' }
        res = self.client.post(TOURNAMENTS_URL, payload)

        exists = Tournament.objects.filter(
            name=payload['name']
        ).exists()
        self.assertTrue(exists)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_game_duplicate_fail(self):
        """Test create duplicate tournament as superuser"""
        Tournament.objects.create(name="Tournament")

        payload = { 'name': 'Tournament' }
        res = self.client.post(TOURNAMENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

