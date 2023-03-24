from django import forms
from analytics.models import SchoolDetails

#class StateForm(forms.Form):
#    state_abv = forms.CharField(label='state_abv', max_length=6,initial='ma')


class StateForm(forms.Form):
    class Meta:
        model = SchoolDetails
        fields=('school_state')
        #SchoolDetails.objects.values_list('school_state').distinct())

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.fields['school_state'] = SchoolDetails.objects.none()



STATE_CHOICES= list(
SchoolDetails.objects.values_list('state_abv','school_state').distinct())

class StateForm(forms.Form):
    state_abv= forms.CharField(label='which state data do you want to visualize?', widget=forms.Select(choices=STATE_CHOICES))