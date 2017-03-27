from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models

class Game(models.Model):
    created = models.DateTimeField(auto_now_add=True)

    def hashid(self):
        return settings.HASHIDS.encode(self.id)

    def get_absolute_url(self):
        return reverse('game', args=(self.hashid(),))

    def suspects(self):
        return self.suspect_set.order_by('id')

    def locations(self):
        return self.location_set.order_by('id')

    def weapons(self):
        return self.weapon_set.order_by('id')

class Suspect(models.Model):
    game = models.ForeignKey(Game)
    name = models.CharField(max_length=100)

    def hashid(self):
        return settings.HASHIDS.encode(self.id)

class Location(models.Model):
    game = models.ForeignKey(Game)
    name = models.CharField(max_length=100)

    def hashid(self):
        return settings.HASHIDS.encode(self.id)

class Weapon(models.Model):
    game = models.ForeignKey(Game)
    name = models.CharField(max_length=100)

    def hashid(self):
        return settings.HASHIDS.encode(self.id)
