from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Game
from blazing.serializers import GameSerializer

GAMES_URL = reverse('blazing:game-list')


class PublicGameTestCase(TestCase):
    """Test publicly available game API"""

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_games(self):
        """Test retrieve games"""
        Game.objects.create(name="New Game")
        Game.objects.create(name="New Game 2")

        res = self.client.get(GAMES_URL)
        games = Game.objects.all()
        serializer = GameSerializer(games, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_required_auth_to_create(self):
        """Test if login is required to create"""
        payload = { 'name': 'Game' }
        res = self.client.post(GAMES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateGameTestCase(TestCase):
    """Test non superuser authorized user game api"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@londonappdev.com',
            'password'
        )
        self.client.force_authenticate(self.user)

    def test_non_superuser_create_game_(self):
        """Test create game as non superuser"""
        payload = { 'name': 'Game' }
        res = self.client.post(GAMES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class PrivateSuperUserGameTestCase(TestCase):
    """Test superuser authorized user game api"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            'test@londonappdev.com',
            'password'
        )
        self.client.force_authenticate(self.user)

    def test_create_game(self):
        """Test create game as superuser"""
        payload = { 'name': 'Game' }
        res = self.client.post(GAMES_URL, payload)

        exists = Game.objects.filter(
            name=payload['name']
        ).exists()
        self.assertTrue(exists)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_game_duplicate_fail(self):
        """Test create duplicate game as superuser"""
        Game.objects.create(name="Game")

        payload = { 'name': 'Game' }
        res = self.client.post(GAMES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

