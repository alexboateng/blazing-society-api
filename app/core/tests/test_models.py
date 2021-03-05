from django.test import TestCase
from django.contrib.auth import get_user_model

from unittest.mock import patch

from core import models


def sample_user(email='test@londonappdev.com', password='testpass'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)

class ModelTests(TestCase):

    def test_create_user_with_email_successfull(self):
        """Test to create user with email address"""
        email = 'test@mail.com'
        password = 'Testpassword'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        email = 'test@LONDONAPPDEV.com'
        user = get_user_model().objects.create_user(email, 'test123')
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_new_superuser(self):
        """Test creating super user"""
        user = get_user_model().objects.create_superuser(
            "test123@mail.com",
            'test123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_games_str(self):
        """Test the Game string representation"""
        game = models.Game.objects.create(
            name='MK11'
        )
        self.assertEqual(str(game), game.name)

    def test_tournament_str(self):
        """Test the Tournament string representation"""
        game = models.Tournament.objects.create(
            name='BS RANK March 2020'
        )
        self.assertEqual(str(game), game.name)