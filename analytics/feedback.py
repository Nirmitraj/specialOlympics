from django.core.mail import send_mail
from django.shortcuts import render, redirect
from .forms import FeedbackForm

def feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            send_mail(
                title,
                description,
                'kr030597@gmail.com',  # From
                ['krnchander47@gmail.com'],  # To
            )
            return redirect('success')
    else:
        form = FeedbackForm()

    return render(request, 'analytics/feedback.html', {'form': form})