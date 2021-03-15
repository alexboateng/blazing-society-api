from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Game, Tournament, Scoreline
from blazing.serializers import GameSerializer, TournamentSerializer, ScorelineSerializer

SCORELINE_URL = reverse('blazing:scoreline-list')


def sample_user(email='test@londonappdev.com', password='testpass'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)

def sample_scoreline(user1, user2, tournament_name = 'BS RANK March 2020', game_name="MK11"):
    game = Game.objects.create(
        name=game_name
    )
    tournament = Tournament.objects.create(
        name= tournament_name
    )
    scoreline = Scoreline.objects.create(
        first_player=user1,
        second_player=user2,
        tournament=tournament,
        game=game,
        first_player_score=5,
        second_player_score=2,
        draw_score=3
    )
    return scoreline

class PublicScorelineTests(TestCase):
    """Test unathenticated blazing apis"""

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_scorelines(self):
        """Test retrieve scorelines"""
        user1 = sample_user()
        user2 = sample_user(email="here@mail.com")
        user3 = sample_user(email="test2@mail.com")
        sample_scoreline(user1=user1, user2=user2)
        sample_scoreline(user1=user1, user2=user3, tournament_name = "FIFA 20", game_name="FIFA 20")

        res = self.client.get(SCORELINE_URL)
        scoreline = Scoreline.objects.all()
        serializer = ScorelineSerializer(scoreline, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_required_auth_to_create(self):
        """Test if login is required to create"""
        user1 = sample_user()
        user2 = sample_user(email="here@mail.com")
        tournament = Tournament.objects.create(
                name='BS RANK March 2020'
            )
        game = Game.objects.create(
                name='MK11'
            )
        payload = {
            'first_player': user1.id,
            'second_player': user2.id,
            'tournament': tournament.id,
            'game': game.id,
            'first_player_score':5,
            'second_player_score':2,
            'draw_score':3
        }
        res = self.client.post(SCORELINE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateScorelineTestCase(TestCase):
    """Test non superuser authorized user game api"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@londonappdev.com',
            'password'
        )
        self.client.force_authenticate(self.user)

    def test_non_superuser_create_scoreline(self):
        """Test create game as non superuser"""
        user2 = sample_user(email="here@mail.com")
        tournament = Tournament.objects.create(
                name='BS RANK March 2020'
            )
        game = Game.objects.create(
                name='MK11'
            )
        payload = {
            'first_player': self.user.id,
            'second_player': user2.id,
            'tournament': tournament.id,
            'game': game.id,
            'first_player_score':5,
            'second_player_score':2,
            'draw_score':3
        }
        res = self.client.post(SCORELINE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class PrivateSuperUserScorelineTestCase(TestCase):
    """Test superuser authorized user game api"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            'test@londonappdev.com',
            'password'
        )
        self.client.force_authenticate(self.user)

    def test_create_scoreline(self):
        """Test create game as superuser"""
        user2 = sample_user(email="here@mail.com")
        tournament = Tournament.objects.create(
                name='BS RANK March 2020'
            )
        game = Game.objects.create(
                name='MK11'
            )

        payload = {
            'first_player': self.user.id,
            'second_player': user2.id,
            'tournament': tournament.id,
            'game': game.id,
            'first_player_score':5,
            'second_player_score':2,
            'draw_score':3
        }
        res = self.client.post(SCORELINE_URL, payload, format='json')

        exists = Scoreline.objects.filter(
            first_player_score=payload['first_player_score']
        ).exists()
        # print(payload)
        # print(res.status_code)
        # print(res.data)
        self.assertTrue(exists)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_scoreline_unique(self):
        """Test create scoreline fails when not unique together as superuser"""

        user2 = sample_user(email="here@mail.com")
        sample_scoreline(user1=self.user, user2=user2)
        # Create same data and submit
        tournament = Tournament.objects.get(
                name='BS RANK March 2020'
            )
        game = Game.objects.get(
                name='MK11'
            )

        payload = {
            'first_player': self.user.id,
            'second_player': user2.id,
            'tournament': tournament.id,
            'game': game.id,
            'first_player_score':5,
            'second_player_score':2,
            'draw_score':3
        }
        res = self.client.post(SCORELINE_URL, payload, format='json')

        exists = Scoreline.objects.filter(
            first_player_score=payload['first_player_score']
        ).exists()
        self.assertTrue(exists)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
