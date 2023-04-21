from django import forms
from analytics.models import SchoolDetails

STATE_CHOICES_RAW= list(
SchoolDetails.objects.values_list('state_abv','school_state').distinct())
STATE_CHOICES = []

for val  in STATE_CHOICES_RAW:
    if val[0]!='-99':
        STATE_CHOICES.append(val)
STATE_CHOICES.append(('all','all'))

implementationlevel = {'all':'all',
                'emerging':'Emerging',
                'developing':'Developing',
                'Full-implementation':'full implementation',
                }

locale = {'all':'all','City':'city','Suburb':'suburb','Rural':'rural'}

years = SchoolDetails.objects.values_list('survey_taken_year',flat=True).distinct()
'''
in company terms 2022 is equal to 14 and the data they started collecting is from 2008
similarly 2021 is equal to 13
logic below is to convert actual year to smaller number (14,13,12...)
so any year - 2008 gives that years smaller value
ex: 2022-2008 =14 
'''
year_dict = {val:'year '+str(val-2008)+' '+str(val) for val in years if type(val) == int and val > 2008 }


schoollevels = {'all':'all','Elementary':'Elementary','High':'High','Middle':'Middle','Preschool':'Preschool'}
class Filters(forms.Form):
    state_abv= forms.CharField(label='State', widget=forms.Select(choices=STATE_CHOICES,attrs={'placeholder': 'Name', 'style': 'width: 300px;', 'class': 'form-control'}))
    implementation_level = forms.CharField(label='Implementation level', widget=forms.Select(choices=implementationlevel.items(),attrs={'placeholder': 'Name', 'style': 'width: 300px;', 'class': 'form-control'}))
    locale__startswith = forms.CharField(label='Locale', widget=forms.Select(choices=locale.items(),attrs={'placeholder': 'Name', 'style': 'width: 300px;', 'class': 'form-control'}))
    gradeLevel_WithPreschool = forms.CharField(label='School level',widget = forms.Select(choices = schoollevels.items(),attrs={'placeholder': 'Name', 'style': 'width: 300px;', 'class': 'form-control'}))
    survey_taken_year= forms.CharField(label='Survey year', widget=forms.Select(choices=year_dict.items(),attrs={'placeholder': 'Name', 'style': 'width: 300px;', 'class': 'form-control'}))