from django.http import JsonResponse
from django.views import View
from analytics.models import SchoolDetails

class GetZipcodesView(View):
    def get(self, request, *args, **kwargs):
        state_abv = request.GET.get('state', None)
        zipcodes = SchoolDetails.objects.values_list('zipcode')

        if state_abv is not None:
            # Assuming you have a model Zipcode that has fields 'zipcode' and 'state_abv'
            zipcodes = list(zipcodes.objects.filter(state_abv=state_abv))
        else:
            zipcodes = []

        return JsonResponse({'zipcodes': zipcodes})