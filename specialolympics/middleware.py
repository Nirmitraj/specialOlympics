from django.middleware.clickjacking import XFrameOptionsMiddleware

class CustomXFrameOptionsMiddleware(XFrameOptionsMiddleware):
    def process_response(self, request, response):
        # Logic to determine if the X-Frame-Options header should be set
        # For example, you can check request.META['HTTP_HOST'] or other conditions
        if "your_condition_here":
            response['X-Frame-Options'] = 'ALLOW-FROM https://iframetester.com/'
        return response