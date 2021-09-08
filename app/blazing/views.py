from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Tournament, Game, Scoreline
from blazing import serializers
from blazing import permissions
from user.serializers import UserSerializer

from django.contrib.auth import get_user_model

from django.db.models import Avg, Count, Min, Sum
from django.db.models import Q


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


class ScorelineViewSet(viewsets.GenericViewSet, 
                    mixins.CreateModelMixin, 
                    mixins.ListModelMixin):
    """Manages Scorelines in database"""
    serializer_class = serializers.ScorelineSerializer
    queryset = Scoreline.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.allowSafeMethods,)

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'create':
            return serializers.ScorelineCreateSerializer
        
        return self.serializer_class

    # def perform_create(self, serializer):
    #     """Create a new recipe"""
    #     validated_data = self.request.data
    #     first_player = validated_data.pop('first_player')
    #     second_player = validated_data.pop('second_player')
    #     tournament = validated_data.pop('tournament')
    #     game = validated_data.pop('game')

    #     TournamentInstance = Tournament.objects.get(id=int(tournament))
    #     GameInstance = Game.objects.get(id=int(game))
    #     First_playerInstance = get_user_model().objects.get(id=int(first_player))
    #     Second_playerInstance = get_user_model().objects.get(id=int(second_player))

    #     serializer.save(
    #         tournament=TournamentInstance,
    #         game=GameInstance,
    #         first_player=First_playerInstance,
    #         second_player=Second_playerInstance
    #     )


class GameStatsViewSet(viewsets.ViewSet):
    """game Stats ViewSet"""

    serializer_class = serializers.ScorelineSerializer

    def list(self, request):
        """Return a hello message."""

        users = get_user_model().objects.all().filter(is_gamer=True)

        tournaments = Tournament.objects.all()

        data = []
        for user in users:
            # Get all user gamers available
            userData = {}
            userData['name'] = user.name
            userData['tournaments'] = []

            # Get tournaments for user
            for tournament in tournaments:
                tournamentData = {}
                tournamentData['name'] = tournament.name
                # Get tournaments games played
                tour_games_played = Scoreline.objects.filter(
                    Q(tournament=tournament.id) & (Q(first_player=user.id) | Q(second_player=user.id))
                ).count()
                tour_user_first_player_score = Scoreline.objects.filter(
                                        Q(tournament=tournament.id) & Q(first_player=user.id)
                                    ).aggregate(Sum('first_player_score'))
                tour_user_second_player_score = Scoreline.objects.filter(
                                        Q(tournament=tournament.id) & Q(second_player=user.id)
                                    ).aggregate(Sum('second_player_score'))
                tour_user_draw_score = Scoreline.objects.filter(
                                        Q(tournament=tournament.id) & (Q(first_player=user.id) | Q(second_player=user.id))
                                    ).aggregate(Sum('draw_score'))

                # Calculate loss
                tour_loss_user_first_player_score = Scoreline.objects.filter(
                                        Q(tournament=tournament.id) & Q(first_player=user.id)
                                    ).aggregate(Sum('second_player_score'))
                tour_loss_user_second_player_score = Scoreline.objects.filter(
                                        Q(tournament=tournament.id) & Q(second_player=user.id)
                                    ).aggregate(Sum('first_player_score'))

                tournamentData['tour_games_played'] = tour_games_played
                tournamentData['tour_total_won'] = int(tour_user_first_player_score['first_player_score__sum'] or 0) + int(tour_user_second_player_score['second_player_score__sum'] or 0)
                tournamentData['tour_total_lost'] = int(tour_loss_user_first_player_score['second_player_score__sum'] or 0) + int(tour_loss_user_second_player_score['first_player_score__sum'] or 0)
                tournamentData['tour_total_draws'] = int(tour_user_draw_score['draw_score__sum'] or 0)

    
                tournamentData['games'] = []
                userData['tournaments'].append(tournamentData)

                # Get all games available for tournament
                games = Game.objects.all()
                for game in games:
                    gameData = {}
                    gameData['name'] = game.name
                    gameData['scoreline'] = []
                    tournamentData['games'].append(gameData)

                    # Get all scorelines available for game
                    scoreline = Scoreline.objects.filter(
                        Q(tournament=tournament.id) & Q(game=game.id) & (Q(first_player=user.id) | Q(second_player=user.id))
                    )
                    scoreline_serializer = serializers.ScorelineSerializer(scoreline, many=True)
                    gameData['scoreline'] = scoreline_serializer.data

                    # Get Win Draws and game played stats
                    user_first_player_score = Scoreline.objects.filter(
                                            Q(tournament=tournament.id) & Q(game=game.id) & Q(first_player=user.id)
                                        ).aggregate(Sum('first_player_score'))
                    user_second_player_score = Scoreline.objects.filter(
                                            Q(tournament=tournament.id) & Q(game=game.id) & Q(second_player=user.id)
                                        ).aggregate(Sum('second_player_score'))
                    user_draw_score = Scoreline.objects.filter(
                                            Q(tournament=tournament.id) & Q(game=game.id) & (Q(first_player=user.id) | Q(second_player=user.id))
                                        ).aggregate(Sum('draw_score'))
                    games_played = Scoreline.objects.filter(
                        Q(tournament=tournament.id) & Q(game=game.id) & (Q(first_player=user.id) | Q(second_player=user.id))
                    ).count()

                    # Calculate loss
                    loss_user_first_player_score = Scoreline.objects.filter(
                                            Q(tournament=tournament.id) & Q(game=game.id) & Q(first_player=user.id)
                                        ).aggregate(Sum('second_player_score'))
                    loss_user_second_player_score = Scoreline.objects.filter(
                                            Q(tournament=tournament.id) & Q(game=game.id) & Q(second_player=user.id)
                                        ).aggregate(Sum('first_player_score'))

                    # Calculate Goals
                    goals_user_first_player_score = Scoreline.objects.filter(
                                            Q(tournament=tournament.id) & Q(game=game.id) & Q(first_player=user.id)
                                        ).aggregate(Sum('first_player_score_goals'))
                    goals_user_second_player_score = Scoreline.objects.filter(
                                            Q(tournament=tournament.id) & Q(game=game.id) & Q(second_player=user.id)
                                        ).aggregate(Sum('second_player_score_goals'))

                    # Calculate Goals Against
                    goals_against_user_first_player_score = Scoreline.objects.filter(
                                            Q(tournament=tournament.id) & Q(game=game.id) & Q(first_player=user.id)
                                        ).aggregate(Sum('second_player_score_goals'))
                    goals_against_user_second_player_score = Scoreline.objects.filter(
                                            Q(tournament=tournament.id) & Q(game=game.id) & Q(second_player=user.id)
                                        ).aggregate(Sum('first_player_score_goals'))

                    # print("-----------------------------------------------")
                    # print(games_played)
                    # print("-----------------------------------------------")


                    gameData['total_won'] = int(user_first_player_score['first_player_score__sum'] or 0) + int(user_second_player_score['second_player_score__sum'] or 0)
                    gameData['total_goals_for'] = int(goals_user_first_player_score['first_player_score_goals__sum'] or 0) + int(goals_user_second_player_score['second_player_score_goals__sum'] or 0)
                    gameData['total_goals_against'] = int(goals_against_user_first_player_score['second_player_score_goals__sum'] or 0) + int(goals_against_user_second_player_score['first_player_score_goals__sum'] or 0)
                    gameData['total_goals_avg'] = int(gameData['total_goals_for'] or 0) - int(gameData['total_goals_against'] or 0)
                    gameData['total_draws'] = int(user_draw_score['draw_score__sum'] or 0)
                    gameData['total_lost'] = int(loss_user_first_player_score['second_player_score__sum'] or 0) + int(loss_user_second_player_score['first_player_score__sum'] or 0)

                    gameData['total_points'] = int(gameData['total_won'] or 0) * 3 + int(gameData['total_draws'] or 0)
                    
                    gameData['games_played'] = games_played


            data.append(userData)

            

        return Response(data)
