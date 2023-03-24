from django import forms

class StateForm(forms.Form):
    state_abv = forms.CharField(label='state_abv', max_length=6,initial='ma')
