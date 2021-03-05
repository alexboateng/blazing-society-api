from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Tournament, Game
from blazing import serializers
from blazing import permissions


class TournamentViewSet(viewsets.GenericViewSet, 
                    mixins.CreateModelMixin, 
                    mixins.ListModelMixin):
    """Manages Tournaments in database"""
    serializer_class = serializers.TournamentSerializer
    queryset = Tournament.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.allowSafeMethods,)


class GameViewSet(viewsets.GenericViewSet, 
                    mixins.CreateModelMixin, 
                    mixins.ListModelMixin):
    """Manages Tournaments in database"""
    serializer_class = serializers.GameSerializer
    queryset = Game.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.allowSafeMethods,)

    