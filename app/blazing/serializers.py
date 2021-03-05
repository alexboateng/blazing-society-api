from rest_framework import serializers

from core.models import Game, Tournament


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