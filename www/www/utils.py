from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404

from .models import Game

def get_game_or_404(hashid):
    try:
        game_id, = settings.HASHIDS.decode(hashid)
    except ValueError:
        raise Http404
    game = get_object_or_404(Game, pk=game_id)
    return game
