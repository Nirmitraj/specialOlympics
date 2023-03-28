from django import forms
from analytics.models import SchoolDetails

STATE_CHOICES_RAW= list(
SchoolDetails.objects.values_list('state_abv','school_state').distinct())
STATE_CHOICES = []

for val  in STATE_CHOICES_RAW:
    if val[0]!='-99':
        STATE_CHOICES.append(val)
        
class StateForm(forms.Form):
    state_abv= forms.CharField(label='which state data do you want to visualize?', widget=forms.Select(choices=STATE_CHOICES))