"""Deployment Script for www.grantjenks.com/clue-game/

"""

import os.path as op
from fabric.api import cd, lcd, env, local, run, settings, sudo, prefix, get

repodir = op.dirname(op.realpath(__file__))
basedir = '/srv/www/clue-game'

env.hosts = ['104.198.0.77']
env.user = 'grantj'


def sync():
    source = op.join(basedir, 'www', 'bin', 'db.sqlite3')
    destination = op.join(repodir, 'www', 'bin', 'db.sqlite3')
    get(source, destination)

    from sys import path
    path.append(op.join(repodir, 'www'))

    from os import environ
    environ.setdefault('DJANGO_SETTINGS_MODULE', 'www.local')

    import django
    django.setup()

    from django.contrib.auth.models import User
    for user in User.objects.all():
        user.set_password('password')
        user.save()

    from django.db import connection
    connection.close()


def test():
    with lcd(op.join(repodir, 'www')):
        local('python -Wall manage.py makemigrations --settings=www.development')
        local('python -Wall manage.py migrate --settings=www.development')
        local('python -Wall manage.py check --settings=www.development')
        local('python -Wall manage.py test --settings=www.development')


def deploy():
    with lcd(repodir):
        local('git pull')
        local('git add -p')
        with settings(warn_only=True):
            local('git commit')
        local('git push')
    
    with cd(op.join(basedir, 'repo')):
        run('git pull')

    with cd(op.join(basedir, 'repo', 'www')):
        with prefix('source %s/env27/bin/activate' % basedir):
            run('python manage.py migrate --settings=www.production')
            run('python manage.py collectstatic --noinput --settings=www.production')

    sudo('supervisorctl signal SIGHUP clue-game:*')
