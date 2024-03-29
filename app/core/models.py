from django.db import models

# For creating user manager classes
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import BaseUserManager

from django.conf import settings

import uuid
import os


class UserManager(BaseUserManager):
    """Manager for user profile"""
    def create_user(self, email, password=None, **extra_fields):
        """Creates and save a new user"""
        if not email:
            raise ValueError('Users must have an email address')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)

        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create superuser profile"""
        user = self.create_user(email, password)

        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Database model for users in the system"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_gamer = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = ['name']

    def get_full_name(self):
        """Retrieve full name of user"""
        return self.name

    def get_short_name(self):
        """Retrieve short name"""
        return self.name

    def __str__(self):
        """Return string representation of user"""
        return self.email


class Game(models.Model):
    """Game model"""
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Tournament(models.Model):
    """Tournament model"""
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Scoreline(models.Model):
    """Blazing tournament scoreline"""
    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE,
        related_name='scorelines'
    )
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name='scorelines'
    )
    first_player = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="first_player_users",
    )
    second_player = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="second_player_users",
    )
    first_player_score = models.IntegerField(default=0)
    second_player_score = models.IntegerField(default=0)
    draw_score = models.IntegerField(default=0)
    first_player_score_goals = models.IntegerField(default=0)
    second_player_score_goals = models.IntegerField(default=0)

    class Meta:
        unique_together = ('tournament', 'game', 'first_player', 'second_player')

    def __str__(self):
        return f"{self.game.name} {self.first_player.name} {self.first_player_score} - {self.second_player.name} {self.second_player_score} "