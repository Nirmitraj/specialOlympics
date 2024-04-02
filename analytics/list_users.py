from django.shortcuts import render
from authenticate.models import CustomUser

def list_users(request):
    users = CustomUser.objects.all() # Fetch all users from the SOD database
    return render(request, 'analytics/users_list.html', {'users': users})