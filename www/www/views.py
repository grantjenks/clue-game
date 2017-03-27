import os
import subprocess as sp
import tempfile as tf

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import NameForm
from .models import Game, Suspect, Location, Weapon
from .utils import get_game_or_404

def index(request):
    if request.method == 'POST':
        game = Game()
        game.save()
        return redirect(game)
    else:
        return render(request, 'www/index.html')

def game(request, hashid):
    game = get_game_or_404(hashid)
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

def preview(request, hashid):
    game = get_game_or_404(hashid)
    return render(request, 'www/preview.html', locals())

def download(request, hashid):
    game = get_game_or_404(hashid)

    if request.method != 'POST':
        return redirect(game)

    handle, filename = tf.mkstemp(prefix='wkhtmltopdf-', suffix='.pdf')
    os.fdopen(handle).close()

    domain = '127.0.0.1:8000' if settings.DEBUG else 'www.grantjenks.com'
    url = 'http://%s/clue-game/%s/preview/' % (domain, hashid)
    args = [
        '/usr/local/bin/wkhtmltopdf', '-O', 'Landscape', '-s', 'Letter',
        '-B', '0', '-L', '0', '-R', '0', '-T', '0', '--background',
        url, filename
    ]
    output = sp.check_output(args, stderr=sp.STDOUT)

    with open(filename, 'rb') as reader:
        data = reader.read()

    response = HttpResponse(data, content_type='application/pdf')
    content_disposition = 'attachment; filename="clue-game-%s.pdf"' % hashid
    response['Content-Disposition'] = content_disposition

    return response
