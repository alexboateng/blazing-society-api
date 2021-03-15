from rest_framework import serializers
from django.contrib.auth import get_user_model

from core.models import Game, Tournament, Scoreline
from user.serializers import UserSerializer

class GameSerializer(serializers.ModelSerializer):
    """Serializer for tag object"""

    class Meta:
        model = Game
        fields = ('id', 'name')
        read_only_fields = ('id',)


class TournamentSerializer(serializers.ModelSerializer):
    """Serializer for Ingredient object"""

    class Meta:
        model = Tournament
        fields = ('id', 'name')
        read_only_fields = ('id',)


class ScorelineSerializer(serializers.ModelSerializer):
    """Serializer for Scoreline object"""
    # tournament =  serializers.StringRelatedField(many=True)
    # game =  serializers.StringRelatedField(many=True)
    tournament =  TournamentSerializer()
    game =  GameSerializer()
    first_player =  UserSerializer()
    second_player =  UserSerializer()
    # tournament = serializers.PrimaryKeyRelatedField(
    #     # many=True,
    #     queryset=Tournament.objects.all()
    # )
    # game = serializers.PrimaryKeyRelatedField(
    #     # many=True,
    #     queryset=Game.objects.all()
    # )
    
    def validate(self, data):
        """Check that the start is before the stop."""
        if data['first_player_score'] + data['draw_score'] + data['second_player_score'] > 10:
            raise serializers.ValidationError("Scoreline cannot be grater than 10")
        return data

    class Meta:
        model = Scoreline
        fields = ('id', 
        'tournament', 
        'game', 
        'first_player', 
        'second_player', 
        'first_player_score',
        'second_player_score',
        'draw_score')
        read_only_fields = ('id',)

class ScorelineCreateSerializer(ScorelineSerializer):
    tournament = serializers.PrimaryKeyRelatedField(
        queryset=Tournament.objects.all()
    )
    game = serializers.PrimaryKeyRelatedField(
        queryset=Game.objects.all()
    )
    first_player =  serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all()
    )
    second_player =  serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all()
    )