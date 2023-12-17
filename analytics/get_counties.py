from django.http import JsonResponse
from django.views import View
from analytics.models import SchoolDetails

class GetCountiesView(View):
    def get(self, request, *args, **kwargs):
        print("Got the function call")
        state_abv = request.GET.get('state', None)
        counties = SchoolDetails.objects.values_list('school_county')

        if state_abv is not None:
            # Assuming you have a model Zipcode that has fields 'zipcode' and 'state_abv'
            counties = list(counties.objects.filter(state_abv=state_abv))
        else:
            counties = []

        return JsonResponse({'counties': counties})