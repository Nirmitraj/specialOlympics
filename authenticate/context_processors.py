from authenticate.models import CustomUser

def user_state(request):
    user_state = None
    if request.user.is_authenticated:
        try:
            user_state = CustomUser.objects.values('state').filter(username=request.user).first().get('state', None)
        except AttributeError:
            # Handle the case where the query doesn't return a result
            user_state = None
    return {'user_state': user_state}