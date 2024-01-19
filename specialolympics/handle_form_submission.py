from django.core.mail import send_mail
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def handle_form_submission(request):
    if request.method == 'POST':
        title = request.POST.get('feedbackTitle')
        requestor = request.POST.get('requestor')
        request_type = request.POST.get('requestType')
        description = request.POST.get('feedbackDescription')

        message = f"Title: {title}\nRequestor: {requestor}\nRequest Type: {request_type}\nDescription: {description}"
        print(message)
        send_mail(
            'Feedback Form Submission',
            message,
            'specialolympics760@gmail.com',
            ['krnchander47@gmail.com'],
        )

        return HttpResponse('Form submitted successfully')

    return HttpResponse('Method not allowed', status=405)