from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render

from .forms import NameForm
from .models import Game, Suspect, Location, Weapon

def index(request):
    if request.method == 'POST':
        game = Game()
        game.save()
        return redirect(game)
    else:
        return render(request, 'www/index.html')

def game(request, hashid):
    game_id, = settings.HASHIDS.decode(hashid)
    game = get_object_or_404(Game, pk=game_id)
    context = {'game': game, 'name_form': NameForm()}

    if request.method == 'POST':
        def add(kind):
            name_form = NameForm(request.POST)
            context['name_form'] = name_form
            if name_form.is_valid():
                name = name_form.cleaned_data['name']
                model = kind(game=game, name=name)
                model.save()
                return True
            
        def delete(kind):
            hashid = request.POST['hashid']
            model_id, = settings.HASHIDS.decode(hashid)
            model = get_object_or_404(kind, pk=model_id)
            model.delete()
            return True
            
        actions = {
            'add-suspect': (add, Suspect),
            'add-location': (add, Location),
            'add-weapon': (add, Weapon),
            'delete-suspect': (delete, Suspect),
            'delete-location': (delete, Location),
            'delete-weapon': (delete, Weapon),
        }
    
        for key, (function, kind) in actions.items():
            if key in request.POST:
                if function(kind):
                    return redirect(game)
        else:
            raise RuntimeError('action not found')

    return render(request, 'www/game.html', context)
