from django import forms
from django_select2 import forms as s2forms
from analytics.models import SchoolDetails
from django_select2.forms import Select2Widget
from collections import OrderedDict
from authenticate.models import CustomUser

STATE_CHOICES_RAW= list(
SchoolDetails.objects.values_list('state_abv','school_state').distinct())
STATE_CHOICES = []

for val in STATE_CHOICES_RAW:
    if val[0] != '-99' and None not in val:
        STATE_CHOICES.append(val)

STATE_CHOICES.sort(key=lambda x: x[0] if x[0] is not None else '')

# Insert the ('all', 'Admin') tuple at the beginning
STATE_CHOICES.insert(0, ('all', 'Admin'))



implementationlevel = {'all':'Unified Sports + Inclusive Youth Leadership + Whole School Engagement',
                '1':'Unified Sports',
                '2':'Inlcusive Youth Leadership',
                '3':'Whole School Engagement',
                '4': 'Unified Sports + Inclusive Youth Leadership',
                '5': 'Unified Sports + Whole School Engagement',
                '6': 'Inclusive Youth Leadership + Whole School Engagement',
                # '7': 'Unified Sports + Inclusive Youth Leadership + Whole School Engagement'
                }

locale = {'all':'All','City':'City','Suburb':'Suburb','Rural':'Rural', 'Town':'Town'}

years = SchoolDetails.objects.values_list('survey_taken_year',flat=True).distinct()
counties = SchoolDetails.objects.values_list('school_county', flat=True)
county_dict = {'all': 'All'}  
county_dict.update({county: county for county in counties  if county is not None and county != '-99' and county != '' and county != '#N/A' and not county.isupper() and '†' not in county})



# print(SchoolDetails.objects.values_list[0])
'''
in company terms 2022 is equal to 14 and the data they started collecting is from 2008
similarly 2021 is equal to 13
logic below is to convert actual year to smaller number (14,13,12...)
so any (- 2008) gives that years smaller value
ex: 2022-2008 =14 
'''
first_year = min(years) if years else None
last_year = max(years) if years else None
year_dict = {val:'Year '+str(val-2008)+' ('+str(val-1)+'-'+(str(val)[-2:]+')') for val in years if type(val) == int and val > 2008}
year_dict = OrderedDict(sorted(year_dict.items(), reverse=True))
# class StateAbvSelect2Widget(s2forms.ModelSelect2MultipleWidget):
#     search_fields = [
#         "state_abv__icontains",
#         "school_state__icontains",
#     ]
schoollevels = {'all':'All','4.00':'Preschool', '1.00':'Elementary', '3.00':'Middle', '2.00':'High',}
class Filters(forms.Form):
    implementation_level = forms.ChoiceField(
        label='Components', 
        widget=forms.Select(attrs={'placeholder': 'Name', 'style': 'width: 300px;', 'class': 'form-control', 'id': 'implementation_drop'}),
        choices=implementationlevel.items()
    )
    locale__startswith = forms.ChoiceField(
        label='Locale', 
        widget=forms.Select(attrs={'placeholder': 'Name', 'style': 'width: 300px;', 'class': 'form-control', 'id': 'locale_drop'}),
        choices=locale.items()
    )
    gradeLevel_WithPreschool = forms.ChoiceField(
        label='School level',
        widget=forms.Select(attrs={'placeholder': 'Name', 'style': 'width: 300px;', 'class': 'form-control', 'id': 'gradeLevel_drop'}),
        choices=schoollevels.items()
    )
    survey_taken_year= forms.ChoiceField(
        label='Survey year', 
        widget=forms.Select(attrs={'placeholder': 'Name', 'style': 'width: 300px;', 'class': 'form-control', 'id': 'survey_drop'}),
        choices=year_dict.items()
    )#   zipcode = forms.MultipleChoiceField(
#         label='Postal code',
#         choices=zipcode_dict.items(),
#         widget=Select2MultipleWidget(
#             attrs={'style': 'width: 300px;', 'id': 'id_zipcodes'}
#             ),
#         required=False,  # Set to False if you want to allow no selection
#         initial=list(zipcode_dict.keys())[0]  # Set the first key in the dictionary as the default value
#     )
    state = 'all'
    school_county = 'all'

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
        if (state == None ):
            self.state = CustomUser.objects.values('state').filter(username=request.user)[0]

        else:
            self.state = state

        

        super().__init__(*args)

        self.fields['state_abv'] = forms.CharField(label='State Program', widget=forms.Select(choices=state,attrs={'placeholder': 'Name', 'style': 'width: 300px;', 'class': 'form-control', 'id': 'state_drop'}))

        # self.fields['state_abv'] = forms.ChoiceField(
        #     label='State Program', 
        #     widget=forms.Select(attrs={'placeholder': 'Name', 'style': 'width: 300px;', 'class': 'form-control', 'id': 'state_drop'}),
        #     choices=state
        # )
        # if state and state[0]:
        counties = SchoolDetails.objects.filter(state_abv=state[0][0]).values_list('school_county', flat=True)
        # else:
            # counties = SchoolDetails.objects.filter(state_abv='MA').values_list('school_county', flat=True)
        county_dict = {'all': 'All'}  
        county_dict.update({county: county for county in counties if county is not None and county != '-99' and county != '' and county != '#N/A' and not county.isupper() and '†' not in county})
        print("NEW COUNTIES", counties)
        self.fields['school_county'] = forms.CharField(
                    label='County', 
                    widget=forms.Select(choices=county_dict.items(), attrs={'placeholder': 'Name', 'style': 'width: 300px;', 'class': 'form-control', 'id': 'county_drop', 'name':"county_drop"}),
                )
    # state_abv= forms.CharField(label='State', widget=forms.Select(choices=state,attrs={'placeholder': 'Name', 'style': 'width: 300px;', 'class': 'form-control'}))


class FeedbackForm(forms.Form):
        requester = forms.CharField(max_length=100)
        REQUEST_TYPES = [
            ('feature_request', 'Feature Request'),
            ('problem', 'Problem'),
            ('question', 'Question'),
        ]

        request_type = forms.ChoiceField(choices=REQUEST_TYPES, label='Request type')
        subject = forms.CharField(max_length=100)
        description = forms.CharField(widget=forms.Textarea)
