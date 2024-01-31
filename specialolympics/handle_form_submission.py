from django.core.mail import send_mail
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMultiAlternatives
from authenticate.models import CustomUser

@csrf_exempt
def handle_form_submission(request):
    if request.method == 'POST':
        title = request.POST.get('feedbackTitle')
        requestor = request.POST.get('requestor')
        request_type = request.POST.get('requestType')
        description = request.POST.get('feedbackDescription')
        state = CustomUser.objects.values('state').filter(username=request.user)[0]
        state=state.get('state','None')

        message = f"""
        <h1>{title}</h1>
        <p><strong>Source:</strong>SO State Dashboard</p>
        <p><strong>Program:</strong> {state}</p>
        <p><strong>Requestor:</strong> {requestor}</p>
        <p><strong>Request Type:</strong> {request_type}</p>
        <p><strong>Description:</strong> {description}</p>
        """

        email = EmailMultiAlternatives(
            title,
            '',  # We can leave the plaintext content empty
            'specialolympics760@gmail.com',
            ['krnchander47@gmail.com'],
        )
        email.attach_alternative(message, "text/html")
        email.send()

        return HttpResponse('Form submitted successfully')

    return HttpResponse('Method not allowed', status=405)