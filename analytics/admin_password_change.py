from django.shortcuts import render, redirect
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from . import AdminPasswordChangeForm

# @permission_required('auth.change_user')
def admin_password_change(request):
    if request.method == 'POST':
        form = AdminPasswordChangeForm.AdminPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            user.set_password(form.cleaned_data['new_password1'])
            user.save()
            messages.success(request, 'Password successfully updated.')
            return redirect('/list_users')
    else:
        print(request.user)
        form = AdminPasswordChangeForm.AdminPasswordChangeForm(user=request.user)
    return render(request, 'analytics/admin_password_change.html', {'form': form})