from django import forms
from authenticate.models import CustomUser
from django.contrib.auth.forms import SetPasswordForm

class AdminPasswordChangeForm(SetPasswordForm):
    user = forms.ModelChoiceField(queryset=CustomUser.objects.all())

    def __init__(self, *args, **kwargs):
        super(AdminPasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['user'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})