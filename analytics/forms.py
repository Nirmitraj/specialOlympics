from django import forms
from django_select2 import forms as s2forms
from analytics.models import SchoolDetails
from django_select2.forms import Select2TagWidget, Select2MultipleWidget

STATE_CHOICES_RAW= list(
SchoolDetails.objects.values_list('state_abv','school_state').distinct())
STATE_CHOICES = []

for val  in STATE_CHOICES_RAW:
    if val[0]!='-99':
        STATE_CHOICES.append(val)
STATE_CHOICES.append(('all','all'))


implementationlevel = {'all':'All',
                '1':'Emerging',
                '2':'Developing',
                '3':'Full implementation',
                }

locale = {'all':'All','City':'City','Suburb':'Suburb','Rural':'Rural'}

years = SchoolDetails.objects.values_list('survey_taken_year',flat=True).distinct()
zipcodes = SchoolDetails.objects.values_list('zipcode', flat=True)
zipcode_dict = {'all': 'All'}  
zipcode_dict.update({zipcode: zipcode for zipcode in zipcodes if zipcode != '-99'})

print(zipcode_dict)

print("=================ZIPCODE TESTING=====================")

# print(SchoolDetails.objects.values_list[0])
'''
in company terms 2022 is equal to 14 and the data they started collecting is from 2008
similarly 2021 is equal to 13
logic below is to convert actual year to smaller number (14,13,12...)
so any (year - 2008) gives that years smaller value
ex: 2022-2008 =14 
'''
first_year = min(years) if years else None
last_year = max(years) if years else None
year_dict = {val:'Year '+str(val-2008)+' ('+str(val-1)+'-'+(str(val)[-2:]+')') for val in years if type(val) == int and val > 2008}

class StateAbvSelect2Widget(s2forms.ModelSelect2MultipleWidget):
    search_fields = [
        "state_abv__icontains",
        "school_state__icontains",
    ]
schoollevels = {'all':'All','1.00':'Elementary','2.00':'High','3.00':'Middle','4.00':'Preschool'}
class Filters(forms.Form):
    implementation_level = forms.CharField(label='Implementation level', widget=forms.Select(choices=implementationlevel.items(),attrs={'placeholder': 'Name', 'style': 'width: 300px;', 'class': 'form-control', 'id': 'implementation_drop'}))
    locale__startswith = forms.CharField(label='Locale', widget=forms.Select(choices=locale.items(),attrs={'placeholder': 'Name', 'style': 'width: 300px;', 'class': 'form-control', 'id': 'locale_drop'}))
    gradeLevel_WithPreschool = forms.CharField(label='School level',widget = forms.Select(choices = schoollevels.items(),attrs={'placeholder': 'Name', 'style': 'width: 300px;', 'class': 'form-control', 'id': 'gradeLevel_drop'}))
    survey_taken_year= forms.CharField(label='Survey year', widget=forms.Select(choices=year_dict.items(),attrs={'placeholder': 'Name', 'style': 'width: 300px;', 'class': 'form-control', 'id': 'survey_drop'}))
#   zipcode = forms.MultipleChoiceField(
#         label='Postal code',
#         choices=zipcode_dict.items(),
#         widget=Select2MultipleWidget(
#             attrs={'style': 'width: 300px;', 'id': 'id_zipcodes'}
#             ),
#         required=False,  # Set to False if you want to allow no selection
#         initial=list(zipcode_dict.keys())[0]  # Set the first key in the dictionary as the default value
#     )
    state = 'all'
    # implementation_level = forms.MultipleChoiceField(
    #     widget=Select2MultipleWidget(attrs={'style': 'width: 300px;'}), 
    #     choices=implementationlevel.items(),
    #     initial=list(implementationlevel.keys())[0]  # Set the first key in the dictionary as the default value
    # )
    # locale__startswith = forms.MultipleChoiceField(
    #     label='Locale',
    #     choices=locale.items(),
    #     widget=Select2MultipleWidget(attrs={'style': 'width: 300px;'}),
    #     required=True,  # Set to False if you want to allow no selection
    #     initial=list(locale.keys())[0]  # Set the first key in the dictionary as the default value
    # )

    # gradeLevel_WithPreschool = forms.MultipleChoiceField(
    #     label='School level',
    #     choices=schoollevels.items(),
    #     widget=Select2MultipleWidget(attrs={'style': 'width: 300px;'}),
    #     required=False,  # Set to False if you want to allow no selection
    #     initial=list(schoollevels.keys())[0]  # Set the first key in the dictionary as the default value
    # )

    # # survey_taken_year = forms.CharField(
    # #     label='Survey year',
    # #     choices=year_dict.items(),
    # #     widget=Select2TagWidget(attrs={'style': 'width: 300px;'}),
    # #     required=False,  # Set to False if you want to allow no selection
    # #     initial=list(year_dict.keys())[0]  
    # # )

    # # survey_taken_year= forms.CharField(label='Survey year', 
    # #                                    widget=forms.Select(choices=year_dict.items(),
    # #                                    attrs={'placeholder': 'Name', 'style': 'width: 300px;', 'class': 'form-control'},
    # #                                     initial=list(year_dict.keys())[0]  ))

    # # survey_taken_year = forms.MultipleChoiceField(

    # #     label= "Survey year",
    # #     widget=Select2TagWidget(choices=year_dict.items()),
    # #     attrs={'placeholder': 'Name', 'style': 'width: 300px;', 'class': 'form-control'},
    # #     initial=list(year_dict.keys())[0]  )
    
    # # gradeLevel_WithPreschool = forms.MultipleChoiceField(
    # #     label='School level',
    # #     choices=schoollevels.items(),
    # #     widget=Select2MultipleWidget(attrs={'style': 'width: 300px;'}),
    # #     required=False,  # Set to False if you want to allow no selection
    # #     initial=list(schoollevels.keys())[0]  # Set the first key in the dictionary as the default value
    # # )
    # survey_taken_year = forms.MultipleChoiceField(
    #     label='School level',
    #     choices=year_dict.items(),
    #     widget=Select2MultipleWidget(attrs={'style': 'width: 300px;'}),
    #     required=False,  # Set to False if you want to allow no selection
    #     initial=list(year_dict.keys())[0]  # Set the first key in the dictionary as the default value
    # )

    # state_abv = forms.MultipleChoiceField(
    #     label='State Program',
    #     choices=STATE_CHOICES,
    #     widget=Select2MultipleWidget(attrs={'style': 'width: 300px;', 'id': 'id_state_abv'}),
    #     required=False,  # Set to False if you want to allow no selection
    #     initial=STATE_CHOICES[0]  # Set the first key in the dictionary as the default value
    # )


  

    def __init__(self, state, *args, **kwargs):
        print('==STATE',state)
        self.state = state
        super().__init__(*args)
        self.fields['state_abv'] = forms.CharField(label='State Program', widget=forms.Select(choices=state,attrs={'placeholder': 'Name', 'style': 'width: 300px;', 'class': 'form-control', 'id': 'state_drop'}))
        zipcodes = SchoolDetails.objects.filter(state_abv='AK').values_list('zipcode', flat=True)
        zipcode_dict = {'all': 'All'}  
        zipcode_dict.update({zipcode: zipcode for zipcode in zipcodes if zipcode != '-99'})

        self.fields['zipcode']= forms.CharField(label='Postal code', widget=forms.Select(choices=zipcode_dict.items(),attrs={'placeholder': 'Name', 'style': 'width: 300px;', 'class': 'form-control', 'id': 'postalCode_drop'}))

    # state_abv= forms.CharField(label='State', widget=forms.Select(choices=state,attrs={'placeholder': 'Name', 'style': 'width: 300px;', 'class': 'form-control'}))

