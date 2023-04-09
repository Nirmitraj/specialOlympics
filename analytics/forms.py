from django import forms
from analytics.models import SchoolDetails

STATE_CHOICES_RAW= list(
SchoolDetails.objects.values_list('state_abv','school_state').distinct())
STATE_CHOICES = []

for val  in STATE_CHOICES_RAW:
    if val[0]!='-99':
        STATE_CHOICES.append(val)
STATE_CHOICES.append(('all','all'))

schoollevels = {'all':'all',
                'emerging':'Emerging',
                'developing':'Developing',
                'Full-implementation':'full implementation',
                }

locale = {'all':'all','City':'city','Suburb':'suburb','Rural':'rural'}

years = dict(SchoolDetails.objects.values_list('survey_taken_year','survey_taken_year').distinct())

class Filters(forms.Form):
    state_abv= forms.CharField(label='State', widget=forms.Select(choices=STATE_CHOICES,attrs={'placeholder': 'Name', 'style': 'width: 300px;', 'class': 'form-control'}))
    implementation_level = forms.CharField(label='Schoollevel', widget=forms.Select(choices=schoollevels.items(),attrs={'placeholder': 'Name', 'style': 'width: 300px;', 'class': 'form-control'}))
    locale__startswith = forms.CharField(label='Locale', widget=forms.Select(choices=locale.items(),attrs={'placeholder': 'Name', 'style': 'width: 300px;', 'class': 'form-control'}))
    survey_taken_year= forms.CharField(label='survey year', widget=forms.Select(choices=years.items(),attrs={'placeholder': 'Name', 'style': 'width: 300px;', 'class': 'form-control'}))