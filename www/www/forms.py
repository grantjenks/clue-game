from django import forms

from .models import Suspect, Location, Weapon

class NameForm(forms.Form):
    name = forms.CharField(max_length=100)
