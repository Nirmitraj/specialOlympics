from django import forms
from analytics.models import SchoolDetails

STATE_CHOICES_RAW= list(
SchoolDetails.objects.values_list('state_abv','school_state').distinct())
STATE_CHOICES = []

for val  in STATE_CHOICES_RAW:
    if val[0]!='-99':
        STATE_CHOICES.append(val)
STATE_CHOICES.append(('all','all'))


implementationlevel = {'all':'All',
                '1':'Emerging',
                '2':'Developing',
                '3':'Full implementation',
                }

locale = {'all':'All','City':'City','Suburb':'Suburb','Rural':'Rural'}

years = SchoolDetails.objects.values_list('survey_taken_year',flat=True).distinct()
'''
in company terms 2022 is equal to 14 and the data they started collecting is from 2008
similarly 2021 is equal to 13
logic below is to convert actual year to smaller number (14,13,12...)
so any (year - 2008) gives that years smaller value
ex: 2022-2008 =14 
'''
year_dict = {val:'Year '+str(val-2008)+' '+str(val) for val in years if type(val) == int and val > 2008 }


schoollevels = {'all':'all','1.00':'Elementary','2.00':'High','3.00':'Middle','4.00':'Preschool'}
class Filters(forms.Form):
    implementation_level = forms.CharField(label='Implementation level', widget=forms.Select(choices=implementationlevel.items(),attrs={'placeholder': 'Name', 'style': 'width: 300px;', 'class': 'form-control'}))
    locale__startswith = forms.CharField(label='Locale', widget=forms.Select(choices=locale.items(),attrs={'placeholder': 'Name', 'style': 'width: 300px;', 'class': 'form-control'}))
    gradeLevel_WithPreschool = forms.CharField(label='School level',widget = forms.Select(choices = schoollevels.items(),attrs={'placeholder': 'Name', 'style': 'width: 300px;', 'class': 'form-control'}))
    survey_taken_year= forms.CharField(label='Survey year', widget=forms.Select(choices=year_dict.items(),attrs={'placeholder': 'Name', 'style': 'width: 300px;', 'class': 'form-control'}))
   
    state = 'all'
    def __init__(self,state,*args):
        print('STATE',state)
        self.state = state
        super().__init__(*args)
        self.fields['state_abv'] = forms.CharField(label='State Program', widget=forms.Select(choices=state,attrs={'placeholder': 'Name', 'style': 'width: 300px;', 'class': 'form-control'}))

    #state_abv= forms.CharField(label='State', widget=forms.Select(choices=state,attrs={'placeholder': 'Name', 'style': 'width: 300px;', 'class': 'form-control'}))

