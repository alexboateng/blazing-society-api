from django.urls import path, include
from rest_framework.routers import DefaultRouter

from blazing import views


router = DefaultRouter()
router.register('tournaments', views.TournamentViewSet)
router.register('games', views.GameViewSet)
# router.register('recipes', views.RecipeViewset)

app_name = 'blazing'

urlpatterns = [
    path('', include(router.urls))
]
