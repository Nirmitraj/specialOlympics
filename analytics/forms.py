from django import forms
from analytics.models import SchoolDetails

STATE_CHOICES_RAW= list(
SchoolDetails.objects.values_list('state_abv','school_state').distinct())
STATE_CHOICES = []

for val  in STATE_CHOICES_RAW:
    if val[0]!='-99':
        STATE_CHOICES.append(val)
STATE_CHOICES.append(('all','all'))

schoollevels = {'emerging':'Emerging',
                'developing':'Developing',
                'Full-implementation':'full implementation',
                'all':'all'}

locale = {'City':'city','Suburb':'suburb','Rural':'rural','all':'all'}

years = dict(SchoolDetails.objects.values_list('survey_taken_year','survey_taken_year').distinct())

class Filters(forms.Form):
    state_abv= forms.CharField(label='State', widget=forms.Select(choices=STATE_CHOICES))
    implementation_level = forms.CharField(label='Schoollevel', widget=forms.Select(choices=schoollevels.items()))
    locale__startswith = forms.CharField(label='Locale', widget=forms.Select(choices=locale.items()))
    survey_taken_year= forms.CharField(label='survey year', widget=forms.Select(choices=years.items()))