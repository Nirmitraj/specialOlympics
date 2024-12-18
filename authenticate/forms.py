from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from .models import CustomUser
from analytics.models import SchoolDetails
from django import forms


class EditProfileForm(UserChangeForm):
    password = forms.CharField(label="", widget=forms.TextInput(attrs={'type':'hidden'}))
    class Meta:
        model = User
        #excludes private information from User
        fields = ('username', 'first_name', 'last_name', 'email','password',)
        
STATE_CHOICES_RAW= list(
SchoolDetails.objects.values_list('school_state','state_abv').distinct())
STATE_CHOICES = []

for val in STATE_CHOICES_RAW:
    if val[0] != '-99' and None not in val:
        STATE_CHOICES.append(val)

STATE_CHOICES.sort(key=lambda x: x[0] if x[0] is not None else '')

# Insert the ('all', 'Admin') tuple at the beginning
STATE_CHOICES.insert(0, ('all', 'Admin'))

class SignUpForm(UserCreationForm):
    email = forms.EmailField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email Address'}), )
    first_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'First Name'}))
    last_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Last Name'}))
    state = forms.CharField(label='State Program', widget=forms.Select(choices=STATE_CHOICES,attrs={'placeholder': 'Name', 'style': 'width: 300px;', 'class': 'form-control'}))

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2','email','state')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'User Name'
        self.fields['username'].label = ''
        self.fields['username'].help_text = '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'

        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password1'].label = ''
        self.fields['password1'].help_text = '<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>'

        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
        self.fields['password2'].label = ''
        self.fields['password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'


STATE_CHOICES_RAW= list(
SchoolDetails.objects.values_list('state_abv','school_state').distinct())
STATE_CHOICES = []

for val in STATE_CHOICES_RAW:
    if val[0]!='-99':
        STATE_CHOICES.append(val)

