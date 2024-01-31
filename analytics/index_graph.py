from django.shortcuts import render
from plotly.offline import plot
import plotly.graph_objects as go
import plotly.express as px
from django.http import HttpResponseRedirect
from django.db.models import Sum,Count,Max
from .forms import Filters
from analytics.models import SchoolDetails
from authenticate.models import CustomUser
import pandas as pd
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views import View
from collections.abc import Iterable
from django.utils.safestring import mark_safe
from django.db.models import Case, When, Value, CharField
from django.db.models import QuerySet
from plotly.graph_objects import Figure, Pie
from io import BytesIO
from reportlab.pdfgen import canvas
from django.http import FileResponse
import imgkit
import plotly.io as pio
from reportlab.lib.pagesizes import letter, landscape
from django.core.cache import cache
import plotly.io as py
import io
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth
from PIL import Image
import tempfile

state_abv_ = 'sc'
    
''' This sends filters in to django querys 
    if all is present in input we remove
    that as it is eqvivalent of all in query'''

# def filter_set(dashboard_filters):
#     filters = []
#     print("filter set", dashboard_filters)

#     for key,val in dashboard_filters.items():
#         if isinstance(val, list):  # if the value is a list, use the __in lookup
#              if all('all' not in s for s in val) and key != "survey_taken_year":
#                 if key == "zipcode":
#                     zipcode_val = list(map(int, val)) 
#                     filters.append((key, zipcode_val))  
#                 else:
#                     filters.append((key, val))  
#              if key == "survey_taken_year":
#                  #convert the list to int
#                  if isinstance(val, list):  # if the value is a list
#                     try:
#                         new_val = list(map(int, val))  # convert all elements in the list to integers
#                         filters.append((key, new_val))  

#                     except ValueError:
#                       pass 
#         else:  # if the value is not a list, just compare it to 'all'
#             if val != 'all':
#                 filters.append((key, val))
#     filters = dict(filters)
#     return filters

def filter_set(dashboard_filters):
    filters = []
    for key,val in dashboard_filters.items():
        if val != 'all' and val != 'All':
            filters.append((key,val))
    filters = dict(filters)
    return filters

def core_exp_percentage(state,year):
    national_sum_1 = dict(SchoolDetails.objects.values_list('unified_sports_component').filter(unified_sports_component=1,survey_taken_year=year).annotate(total = Count('unified_sports_component'))).get(True,0)
    national_sum_2 = dict(SchoolDetails.objects.values_list('youth_leadership_component').filter(youth_leadership_component=1,survey_taken_year=year).annotate(total = Count('youth_leadership_component'))).get(True,0)
    national_sum_3 = dict(SchoolDetails.objects.values_list('whole_school_component').filter(whole_school_component=1,survey_taken_year=year).annotate(total = Count('whole_school_component'))).get(True,0)
    state_sum_1=dict(SchoolDetails.objects.values_list('unified_sports_component').filter(state_abv=state,unified_sports_component=1,survey_taken_year=year).annotate(total = Count('unified_sports_component'))).get(True,0)
    state_sum_2=dict(SchoolDetails.objects.values_list('youth_leadership_component').filter(state_abv=state,youth_leadership_component=1,survey_taken_year=year).annotate(total = Count('youth_leadership_component'))).get(True,0)
    state_sum_3=dict(SchoolDetails.objects.values_list('whole_school_component').filter(state_abv=state,whole_school_component=1,survey_taken_year=year).annotate(total = Count('whole_school_component'))).get(True,0)
    national_sum = national_sum_1 + national_sum_2 + national_sum_3
    state_sum = state_sum_1+state_sum_2 +state_sum_3
    return national_sum,state_sum

def core_experience_data(dashboard_filters,key,range,survey_year=None):
    select_names = {'sports':'unified_sports_component',
                    'leadership':'youth_leadership_component',
                    'whole_school':'whole_school_component'}
    
    filters = filter_set(dashboard_filters)
    filters_national=filter_set(dashboard_filters)
    # print("CHECK", filters)
    if survey_year:
        # print("CHECK1", filters_national)

        filters["survey_taken_year"] = survey_year
        national_sum,state_sum = core_exp_percentage(state=filters['state_abv'],year=survey_year)
    if range == 'national':
        # print("CHECK2", filters_national)

        filters_national["survey_taken_year"] = survey_year
        filters_national.pop('state_abv')
        filters_national.pop('county', None)
        filters = filters_national
    # print("Check 3", filters_national)
    filters_national = add_in_forFilters(filters_national)
    filters = add_in_forFilters(filters)

    # print("Check 4", filters_national)
    if key:#key value for selectnames dictionary
        # print('working this one?')
        data = dict(SchoolDetails.objects.values_list(select_names[key]).filter(**filters).annotate(total = Count(select_names[key])))
        data = data.get(True,0) #considering only participated people
        print(data)
        if survey_year:
            if filters.get('state_abv',False):
                try:
                    #state percent
                    # print('state_sum:',data,select_names[key],survey_year)
                    return round((data/state_sum)*100,2)
                except ZeroDivisionError:
                    return 0
            else:
                try:
                    #national percent            
                    # print('national_sum:',data,select_names[key],survey_year)
                    return round((data/national_sum)*100,2)
                except ZeroDivisionError:
                    return 0
            
        return data
    else:
        return 0

def survey_years():


    survey_years = SchoolDetails.objects.values_list('survey_taken_year',flat=True).distinct().order_by('survey_taken_year')
    return list(survey_years)


def core_experience_year_raw_data(dashboard_filters):
    survey_year= survey_years()
    response = {'sports':[],'leadership':[],'whole_school':[],'survey_year':survey_year,'state_sports':[],'state_leadership':[],'state_whole_school':[]}
    for year in survey_year:
        response['sports'].append(core_experience_year_raw_data_values(dashboard_filters,'sports',survey_year=year,range='national'))
        response['leadership'].append(core_experience_year_raw_data_values(dashboard_filters,'leadership',survey_year=year,range='national'))
        response['whole_school'].append(core_experience_year_raw_data_values(dashboard_filters,'whole_school',survey_year=year,range='national'))
        response['state_sports'].append(core_experience_year_raw_data_values(dashboard_filters,'sports',survey_year=year,range='state'))
        response['state_leadership'].append(core_experience_year_raw_data_values(dashboard_filters,'leadership',survey_year=year,range='state'))
        response['state_whole_school'].append(core_experience_year_raw_data_values(dashboard_filters,'whole_school',survey_year=year,range='state'))            

    return response

def core_experience_year_raw_data_values(dashboard_filters, key, range, survey_year=None):

    select_names = {
        'sports': 'unified_sports_component',
        'leadership': 'youth_leadership_component',
        'whole_school': 'whole_school_component'
    }
    
    filters = filter_set(dashboard_filters)
    filters_national = filter_set(dashboard_filters)
    
    if survey_year:
        filters["survey_taken_year"] = survey_year
        national_sum, state_sum = core_exp_percentage(state=filters['state_abv'], year=survey_year)
    
    if range == 'national':
        filters_national["survey_taken_year"] = survey_year
        filters_national.pop('state_abv')
        filters_national.pop('county', None)
        filters = filters_national
    
    filters_national = add_in_forFilters(filters_national)
    filters = add_in_forFilters(filters)
    
    if key:  # key value for selectnames dictionary
        data = dict(SchoolDetails.objects.values_list(select_names[key]).filter(**filters).annotate(total=Count(select_names[key])))
        data = data.get(True, 0)  # considering only participated people
        
        return data  # Return the raw value directly
    else:
        return 0


def core_experience_year_data(dashboard_filters):
    survey_year= survey_years()
    # print("survey_year", survey_year)
    response = {'sports':[],'leadership':[],'whole_school':[],'survey_year':survey_year,'state_sports':[],'state_leadership':[],'state_whole_school':[]}
    for year in survey_year:
        response['sports'].append(core_experience_data(dashboard_filters,'sports',survey_year=year,range='national'))
        response['leadership'].append(core_experience_data(dashboard_filters,'leadership',survey_year=year,range='national'))
        response['whole_school'].append(core_experience_data(dashboard_filters,'whole_school',survey_year=year,range='national'))
        response['state_sports'].append(core_experience_data(dashboard_filters,'sports',survey_year=year,range='state'))
        response['state_leadership'].append(core_experience_data(dashboard_filters,'leadership',survey_year=year,range='state'))
        response['state_whole_school'].append(core_experience_data(dashboard_filters,'whole_school',survey_year=year,range='state'))            
    return response


def survey_response_year_data(dashboard_filters):
    # survey_year= survey_years()
    # print("survey_year", survey_year)
    # for year in survey_year:
    #     response['national'].append(core_experience_data(dashboard_filters,'sports',survey_year=year,range='national'))
    #     response['state'].append(core_experience_data(dashboard_filters,'sports',survey_year=year,range='state'))
    # return response


    filters = filter_set(dashboard_filters)
    survey_year = survey_years()
    # print(survey_year)
    response = {'national_yes':[0]*len(survey_year), 'national_no':[0]*len(survey_year), 'survey_year':[0]*len(survey_year),'state_yes':[0]*len(survey_year), 'state_no':[0]*len(survey_year)}
    index = 0
    filters = filter_set(dashboard_filters)
    filters.pop('state_abv')
    if "county" in filters:
        filters.pop('county')
    
    for year in survey_year:
        filters['survey_taken_year'] = year
        # print(filters)
        national_data = SchoolDetails.objects.values('survey_taken', 'survey_taken_year').filter(**filters).exclude(school_state='-99').annotate(total=Count('survey_taken')).order_by('survey_taken_year')        #  = SchoolDetails.objects.values('implementation_level','survey_taken_year').filter(**filters).annotate(total = Count('implementation_level')).order_by('implementation_level')
        for val in national_data:
            if val['survey_taken']:
                response["national_yes"][index] = val.get('total',0)
                response["survey_year"][index] = val.get('survey_taken_year',0)
            else:
                response["national_no"][index] = val.get('total',0)


        index+=1

    print(response)

    index = 0
    filters_state = filter_set(dashboard_filters)
    if "county" in filters_state:
        filters_state.pop('county')
    filters_state = add_in_forFilters(filters_state)
    
    for year in survey_year:
        filters_state['survey_taken_year'] = year
        state_data = SchoolDetails.objects.values('survey_taken', 'survey_taken_year').filter(**filters_state).exclude(school_state='-99').annotate(total=Count('survey_taken')).order_by('survey_taken_year')
        print("=====TEST1=====", state_data,filters_state)

        for val in state_data:
            if val['survey_taken']:
                response["state_yes"][index] = val.get('total',0)
            else:
                response["state_no"][index] = val.get('total',0)
        index+=1
    
    print(response)

    # # print('implementation_level_data',response)
    national_sum=''
    state_sum=''

    return response

def survey_response_year_percentage_data(response):
    # Calculate the percentage for 'national_yes'
    national_percentages = [
        round((yes / (yes + no)) * 100, 2) if (yes + no) > 0 else 0
        for yes, no in zip(response['national_yes'], response['national_no'])
    ]
    
    # Calculate the percentage for 'state_yes'
    state_percentages = [
        round((yes / (yes + no)) * 100, 2) if (yes + no) > 0 else 0
        for yes, no in zip(response['state_yes'], response['state_no'])
    ]
    
    # Update the response dictionary with the calculated percentages
    response['national_yes'] = national_percentages
    response['state_yes'] = state_percentages
    
    # Return only the 'national_yes' and 'state_yes' percentage values
    return {
        'national': response['national_yes'],
        'state': response['state_yes'],
        'survey_year': response['survey_year']
    }

def implementation_level_data(dashboard_filters):
    filters = filter_set(dashboard_filters)
    survey_year = survey_years()
    # print(survey_year)
    response = {"emerging":[0]*len(survey_year),"developing":[0]*len(survey_year),"full_implement":[0]*len(survey_year),"survey_year":[0]*len(survey_year),
                "state_emerging":[0]*len(survey_year),"state_developing":[0]*len(survey_year),"state_full_implement":[0]*len(survey_year)}
    index = 0
    filters = filter_set(dashboard_filters)
    filters.pop('state_abv')
    if "county" in filters:
        filters.pop('county')
    
    for year in survey_year:
        filters['survey_taken_year'] = year
        # print(filters)
        national_data = SchoolDetails.objects.values('implementation_level','survey_taken_year').filter(**filters).annotate(total = Count('implementation_level')).order_by('implementation_level')
        print("=========TEST=======", national_data,filters)
        for val in national_data:
            if val['implementation_level'] in ['1','1.00']:
                response["emerging"][index] = val.get('total',0)
            elif val['implementation_level'] in ['2','2.00']:
                response["developing"][index] = val.get('total',0)
            elif val['implementation_level'] in ['3','3.00']:
                response["full_implement"][index] = val.get('total',0)
                response["survey_year"][index] = val.get('survey_taken_year',0)
        index+=1

    index = 0
    filters_state = filter_set(dashboard_filters)
    filters_state = add_in_forFilters(filters_state)
    for year in survey_year:
        filters_state['survey_taken_year'] = year
        state_data = SchoolDetails.objects.values('implementation_level','survey_taken_year').filter(**filters_state).annotate(total = Count('implementation_level')).order_by('implementation_level')

        for val in state_data:
            if val['implementation_level'] in ['1','1.00']:
                response["state_emerging"][index] = val.get('total',0)
            elif val['implementation_level'] in ['2','2.00']:
                response["state_developing"][index] = val.get('total',0)
            elif val['implementation_level'] in ['3','3.00']:
                response["state_full_implement"][index] = val.get('total',0)
        index+=1

    # print('implementation_level_data',response)
    national_sum=''
    state_sum=''

    return response


def implementation_level_percentages(response):
    for i in range(0,len(response['survey_year'])):
            total=0
            for val in ['emerging','developing','full_implement']:
                total += response[val][i]
            for val in ['emerging','developing','full_implement']:
                # print(total)
                try:
                    response[val][i]=round((response[val][i]/total)*100,2)
                except ZeroDivisionError:
                    response[val][i]=0

    for i in range(0,len(response['survey_year'])):
            total=0
            for val in ['state_emerging','state_developing','state_full_implement']:
                total += response[val][i]
            for val in ['state_emerging','state_developing','state_full_implement']:
                # print(total)
                try:
                    response[val][i]=round((response[val][i]/total)*100,2)
                except ZeroDivisionError:
                     response[val][i]=0

    return response
import copy

def implementation_level(dashboard_filters, getImage = False):
    raw_data=implementation_level_data(dashboard_filters)
    print(raw_data, "===========RAW DATA==============")
    data = implementation_level_percentages(copy.deepcopy(raw_data))
    # colors = ['rgba(200, 200, 220, 0.8)', 'rgba(168, 184, 134, 0.8)', 'rgba(170, 180, 200, 0.8)', 'rgba(109, 154, 168, 0.8)', 'rgba(120, 130, 160, 0.8)', 'rgba(140, 138, 173, 0.8)']     # Define your colors here with opacity
    print(data, "===========data==============")

    # print("IMPLEVEL:",data)
    df = pd.DataFrame(data)
    print(df, "===========df==============")

    print('SURVEY YEAR',(df == 0).all())
    print("end")
    print(raw_data, "CHECK RAW DATA")
    # fig = px.line(df, x=df['survey_year'], y=df['emerging'], labels={"survey_year":"year","emerging":"Implementation Level"})#color???
    fig = go.Figure()
    # hovertemplate='Year: %{x}<br>Emerging: %{y}%<br>Raw Data: %{customdata}<extra></extra>'
    fig.add_scatter(x=df['survey_year'],y=df['state_emerging'].round(0), customdata=raw_data['state_emerging'],
        hovertemplate=(
        "%{x}, %{y}%, %{customdata} schools"
         ), name="{0} Emerging".format(dashboard_filters['state_abv']))   
    fig.add_scatter(x=df['survey_year'],y=df['state_developing'].round(0),customdata=raw_data['state_developing'],
        hovertemplate=(
        "%{x}, %{y}%, %{customdata} schools"
         ), name="{0} Developing".format((dashboard_filters['state_abv'])))   
    fig.add_scatter(x=df['survey_year'],y=df['state_full_implement'].round(0), customdata=raw_data['state_full_implement'],
        hovertemplate=(
        "%{x}, %{y}%, %{customdata} schools"
         ), name="{0} Full Implementation".format(dashboard_filters['state_abv']))

    fig.add_scatter(x=df['survey_year'],y=df['emerging'].round(0), customdata=raw_data['emerging'],
        hovertemplate=(
        "%{x}, %{y}%, %{customdata} schools"
         ), name="Emerging (National)", visible='legendonly')
    fig.add_scatter(x=df['survey_year'],y=df['developing'].round(0), customdata=raw_data['developing'],
        hovertemplate=(
        "%{x}, %{y}%, %{customdata} schools"
         ), name="Developing (National)" , visible='legendonly')#color="developing")
    fig.add_scatter(x=df['survey_year'],y=df['full_implement'].round(0), customdata=raw_data['full_implement'],
        hovertemplate=(
        "%{x}, %{y}%, %{customdata} schools"
         ), name="Full Implementation (National)".format(dashboard_filters['state_abv']), visible='legendonly')#,color="full_implemention")
    title_name = 'Implementation level over time,<br> National vs. {0} State Program'.format(dashboard_filters['state_abv'])

# for i in range(0,len(response['survey_year'])):
#             total=0
#             for val in ['emerging','developing','full_implement']:
#                 total += response[val][i]
#             for val in ['emerging','developing','full_implement']:
#                 # print(total)
#                 try:
#                     response[val][i]=round((response[val][i]/total)*100,2)
#                 except ZeroDivisionError:
#                     response[val][i]=0

#     for i in range(0,len(response['survey_year'])):
#             total=0
#             for val in ['state_emerging','state_developing','state_full_implement']:
#                 total += response[val][i]
#             for val in ['state_emerging','state_developing','state_full_implement']:
    fig.update_layout( 
    title={
        'text': title_name,
        # 'y': 0.95,  # Adjust the y position of the title (0 - bottom, 1 - top)
        # 'x': 0.5  # Adjust the x position of the title (0 - left, 0.5 - center, 1 - right)

        "x": 0.5,  # Adjust the x position of the title (0 - left, 0.5 - center, 1 - right)
        "y": 0.9,  # Adjust the y position of the title (0 - bottom, 1 - top)
        "yanchor": "top",  # Anchor point of the title (aligned to the top)

    },
    legend=dict(
        orientation="h",
    ),
    xaxis = dict (
        tickmode='linear',
        tick0 = min(df['survey_year']),
        dtick=1
    ),
    yaxis = dict (
        range=[0,100],
        title="Percentage value (%)",  # Add this line
    ),
    margin=dict(
        t=100
    ),

    )
    plot_div = plot(fig, output_type='div', include_plotlyjs=False)
    # print("imp level yoo?")
    if getImage:
        img_bytes = io.BytesIO()
        py.write_image(fig, img_bytes, format='png')
        img_bytes.seek(0)
        return img_bytes
    else:
        if (df == 0).all().all():
            return None
        return plot_div

def add_in_forFilters(new_filters):
    filters = []
    for key,val in new_filters.items():
             if isinstance(val, list):  # if the value is a list, use the __in lookup
                if  key != "locale__startswith":
                    filters.append((f"{key}__in", val))
                else:
                    filters.append((key, val))  
             else:
                filters.append((key, val))  
    filters = dict(filters)
    return filters

def school_suvery_data(dashboard_filters, isAdmin):
    new_filters= filter_set(dashboard_filters)
    # print("PRIIINNTTTT", new_filters)
    # state = CustomUser.objects.values('state').filter(username=request.user)[0]
    if isAdmin:
        new_filters.pop('state_abv',None) # as this graph is for all states we remove state filter for this
    new_filters.pop('county',None)
    # print('Filterssssss',new_filters)
    filters = add_in_forFilters(new_filters)
    
    # print(filters)

    return SchoolDetails.objects.values('school_state','survey_taken').filter(**filters).exclude(school_state='-99').annotate(total = Count('survey_taken')).order_by('school_state')

def school_suvery_school_year_data(dashboard_filters, isAdmin):
    new_filters= filter_set(dashboard_filters)
    # print("PRIIINNTTTTI", new_filters)
    if isAdmin:
        new_filters.pop('state_abv',None) # as this graph is for all states we remove state filter for this
    new_filters.pop('county',None)
    new_filters.pop('survey_taken_year',None)

    # print('FilterssssssI',new_filters)
    filters = add_in_forFilters(new_filters)
    
    # print(filters)
    
    return SchoolDetails.objects.values('school_state','survey_taken', 'survey_taken_year').filter(**filters).exclude(school_state='-99').annotate(total = Count('survey_taken')).order_by('school_state')

def school_suvery_implementation_level_data(dashboard_filters, isAdmin):
    new_filters= filter_set(dashboard_filters)
    # print("PRIIINNTTTTI", new_filters)
    if isAdmin:
     new_filters.pop('state_abv',None) # as this graph is for all states we remove state filter for this
    new_filters.pop('county',None)
    # print('FilterssssssI',new_filters)
    filters = add_in_forFilters(new_filters)
    
    # print(filters)
    
    return SchoolDetails.objects.values('school_state','survey_taken', 'implementation_level').filter(**filters).exclude(school_state='-99').annotate(total = Count('survey_taken')).order_by('school_state')

def school_suvery_locale_data(dashboard_filters, isAdmin):
    new_filters= filter_set(dashboard_filters)
    # print("PRIIINNTTTTI", new_filters)
    if isAdmin:
        new_filters.pop('state_abv',None) # as this graph is for all states we remove state filter for this
    new_filters.pop('county',None)
    # print('FilterssssssI',new_filters)
    filters = add_in_forFilters(new_filters)
    
    print(filters)
    
    school_surveys = SchoolDetails.objects.values('school_state','survey_taken').filter(**filters).exclude(school_state='-99', locale='-99')
    school_surveys = school_surveys.annotate(
        grouped_locale=Case(
            When(locale__startswith='City', then=Value('City')),
            When(locale__startswith='Rural', then=Value('Rural')),
            When(locale__startswith='Suburb', then=Value('Suburb')),
            When(locale__startswith='Town', then=Value('Town')),
            default=Value('Other'),
            output_field=CharField(),
        )
    )

    return school_surveys.values('school_state', 'survey_taken', 'grouped_locale').annotate(total = Count('survey_taken')).order_by('school_state')

def school_suvery_school_data(dashboard_filters, isAdmin):
    new_filters= filter_set(dashboard_filters)
    # print("PRIIINNTTTTI", new_filters)
    if isAdmin:
        new_filters.pop('state_abv',None) # as this graph is for all states we remove state filter for this
    new_filters.pop('county',None)
    # print('FilterssssssI',new_filters)
    filters = add_in_forFilters(new_filters)
    
    # print(filters)
    
    return SchoolDetails.objects.values('school_state','survey_taken','gradeLevel_WithPreschool').filter(**filters).exclude(school_state='-99').annotate(total = Count('survey_taken')).order_by('school_state')

def school_survey_year(dashboard_filters, isAdmin = False):
    school_surveys = school_suvery_school_year_data(dashboard_filters, isAdmin)
    data_json={}
    data_json_value={}

    totals = {}
    print(school_surveys)
    for val in school_surveys:
        if val['school_state'] not in data_json.keys():
            data_json[val['school_state']] = {}
            data_json_value[val['school_state']] = {}
        if str(val['survey_taken']) not in data_json[val['school_state']].keys():
            data_json[val['school_state']][str(val['survey_taken'])] = {}
            data_json_value[val['school_state']][str(val['survey_taken'])] = {}
            totals[(val['school_state'], str(val['survey_taken']))] = 0

        data_json[val['school_state']][str(val['survey_taken'])][val['survey_taken_year']] = val['total']
        data_json_value[val['school_state']][str(val['survey_taken'])][val['survey_taken_year']] = val['total']
        totals[(val['school_state'], str(val['survey_taken']))] += val['total']
    
    print("========RESULT========")
    print(data_json)
    print(totals)
    for state, surveys in data_json.items():
        for survey, grades in surveys.items():
            for grade, total in grades.items():
                data_json[state][survey][grade] = round((total / totals[(state, survey)]) * 100, 0)
                data_json_value[state][survey][grade] = total
                print(data_json)
            
        school_state = list(data_json.keys())
    
    survey_1 = []
    survey_2 = []
    survey_3 = []
    survey_4 = []
    survey_5 = []
    survey_6 = []
    survey_1_value = []
    survey_2_value = []
    survey_3_value = []
    survey_4_value = []
    survey_5_value = []
    survey_6_value = []
    for state in school_state:
        # Get the data for each group, or default to 0 if the group doesn't exist

        survey_1.append(data_json[state].get('True', {}).get(2018, 0))
        survey_2.append(data_json[state].get('True', {}).get(2019, 0))
        survey_3.append(data_json[state].get('True', {}).get(2020, 0))
        survey_4.append(data_json[state].get('True', {}).get(2021, 0))
        survey_5.append(data_json[state].get('True', {}).get(2022, 0))
        survey_6.append(data_json[state].get('True', {}).get(2023, 0))
        survey_1_value.append(data_json_value[state].get('True', {}).get(2018, 0))
        survey_2_value.append(data_json_value[state].get('True', {}).get(2019, 0))
        survey_3_value.append(data_json_value[state].get('True', {}).get(2020, 0))
        survey_4_value.append(data_json_value[state].get('True', {}).get(2021, 0))
        survey_5_value.append(data_json_value[state].get('True', {}).get(2022, 0))
        survey_6_value.append(data_json_value[state].get('True', {}).get(2023, 0))
        print(survey_5)
      

    traces = [
    {"x": school_state, "y": survey_1, "name": '2018', "trace": None, "custom_data": survey_1_value},
    {"x": school_state, "y": survey_2, "name": '2019', "trace": None, "custom_data": survey_2_value},
    {"x": school_state, "y": survey_3, "name": '2020', "trace": None, "custom_data": survey_3_value},
    {"x": school_state, "y": survey_4, "name": '2021', "trace": None, "custom_data": survey_4_value},
    {"x": school_state, "y": survey_5, "name": '2022', "trace": None, "custom_data": survey_5_value},
    {"x": school_state, "y": survey_6, "name": '2023', "trace": None, "custom_data": survey_6_value}

    ]

    # Sort the traces based on their total values
    colors = ['rgba(200, 200, 220, 0.8)', 'rgba(168, 184, 134, 0.8)', 'rgba(170, 180, 200, 0.8)', 'rgba(109, 154, 168, 0.8)', 'rgba(120, 130, 160, 0.8)', 'rgba(140, 138, 173, 0.8)']     # Define your colors here with opacity

    # Create the actual traces
    for i, trace in enumerate(traces):
        trace["trace"] = go.Bar(x=trace["x"], y=trace["y"], name=trace["name"], customdata=trace["custom_data"],
            hovertemplate='%{y}%, %{customdata} schools, %{x}', offsetgroup=1,     marker=dict(color=colors[i])  # Use the colors list here
)

    traces.sort(key=lambda x: sum(x["y"]), reverse=True)

    # Calculate the total for each state
    survey_total = [sum(x) for x in zip(survey_1, survey_2, survey_3, survey_4, survey_5, survey_6)]

    # Create the trace for the total

    # Create the figure and add the traces
    # Note: The total trace should be added first so that it's behind the other bars
    year = dashboard_filters['survey_taken_year']
    print('YEAR',year)
    # years_str = ', '.join(map(str, year))  # convert the array to a string
    # years_minus_2008 = [int(year1) - 2008 for year1 in year]  # subtract 2008 from each year
    # formatted_year_str = ', '.join(map(str, years_minus_2008))
    # print('YEAR1',formatted_year_str)
    # print('YEAR2',years_minus_2008)
    # Create the layout for the plot
    layout = dict(
        title='Year {0} ({1}) State Program response rate compared by Survey Year'.format(int(year)-2008,(str(int(year)-1)+'-'+str(year)[-2:])),
        yaxis=dict(range=[0, 100]),
        barmode='group',
    )

    # Create the figure and add the traces
    fig = go.Figure(data=[trace["trace"] for trace in traces], layout=layout)

    # Update the figure layout
    fig.update_layout(width=1400, height=500)

    # Generate the plot
    plot_div = plot(fig, output_type='div', include_plotlyjs=False)

    return plot_div


def school_survey_school_level(dashboard_filters, isAdmin = False):

    school_surveys = school_suvery_school_data(dashboard_filters, isAdmin)
    # print("school survey", school_surveys)
    data_json={}
    # if 'school_state__in' in data_json.keys():
    #     for val in school_surveys:
    #         if val['school_state__in'] not in data_json.keys():
    #             data_json[val['school_state__in']] = {}
    #         #data_json[val['school_state']][val['survey_taken']] = 0
    #         data_json[val['school_state__in']][str(val['survey_taken__in'])]=val['total']
    # else:
    totals = {}
    data_json_value={}

    for val in school_surveys:
        if val['school_state'] not in data_json.keys():
            data_json[val['school_state']] = {}
            data_json_value[val['school_state']] = {}
        if str(val['survey_taken']) not in data_json[val['school_state']].keys():
            data_json[val['school_state']][str(val['survey_taken'])] = {}
            data_json_value[val['school_state']][str(val['survey_taken'])] = {}
            totals[(val['school_state'], str(val['survey_taken']))] = 0

        data_json[val['school_state']][str(val['survey_taken'])][val['gradeLevel_WithPreschool']] = val['total']
        data_json_value[val['school_state']][str(val['survey_taken'])][val['gradeLevel_WithPreschool']] = val['total']
        totals[(val['school_state'], str(val['survey_taken']))] += val['total']

    # Convert to percentages
    for state, surveys in data_json.items():
        for survey, grades in surveys.items():
            for grade, total in grades.items():
                data_json[state][survey][grade] = round((total / totals[(state, survey)]) * 100, 0)
                data_json_value[state][survey][grade] = total 
        school_state = list(data_json.keys())
        # school_state =(list(data_json.keys()))[0]

    # print("school_state", school_state, dashboard_filters, data_json)
    #convert to percentages
    # Initialize lists to store the data for each group
    survey_1 = []
    survey_2 = []
    survey_3 = []
    survey_4 = []
    survey_1_value = []
    survey_2_value = []
    survey_3_value = []
    survey_4_value = []

    # Iterate over each state
    for state in school_state:
        # Get the data for each group, or default to 0 if the group doesn't exist
        survey_1.append(data_json[state].get('True', {}).get('1.00', 0))
        survey_2.append(data_json[state].get('True', {}).get('2.00', 0))
        survey_3.append(data_json[state].get('True', {}).get('3.00', 0))
        survey_4.append(data_json[state].get('True', {}).get('4.00', 0))
        survey_1_value.append(data_json_value[state].get('True', {}).get('1.00', 0))
        survey_2_value.append(data_json_value[state].get('True', {}).get('2.00', 0))
        survey_3_value.append(data_json_value[state].get('True', {}).get('3.00', 0))
        survey_4_value.append(data_json_value[state].get('True', {}).get('4.00', 0))
        # survey_none.append(data_json[state].get('False', {}).get(None, 0))

    # Create the traces for the plot
    # trace_1 = go.Bar(x=school_state, y=survey_1, name='Emerging (Yes)')
    # trace_2 = go.Bar(x=school_state, y=survey_2, name='Developing (Yes)')
    # trace_3 = go.Bar(x=school_state, y=survey_3, name='Full Implementation (Yes)')
    # trace_none = go.Bar(x=school_state, y=survey_none, name='None')

    traces = [
    {"x": school_state, "y": survey_1, "name": 'Elementary', "trace": None, "custom_data": survey_1_value},
    {"x": school_state, "y": survey_2, "name": 'High', "trace": None, "custom_data": survey_2_value},
    {"x": school_state, "y": survey_3, "name": 'Middle', "trace": None, "custom_data": survey_3_value},
    {"x": school_state, "y": survey_4, "name": 'Preschool', "trace": None, "custom_data": survey_4_value}

    ]

    # Sort the traces based on their total values
    colors = ['rgba(200, 200, 220, 0.8)', 'rgba(168, 184, 134, 0.8)', 'rgba(170, 180, 200, 0.8)', 'rgba(109, 154, 168, 0.8)', 'rgba(120, 130, 160, 0.8)', 'rgba(140, 138, 173, 0.8)']     # Define your colors here with opacity

    # Create the actual traces
    for i, trace in enumerate(traces):
        trace["trace"] = go.Bar(x=trace["x"], y=trace["y"], name=trace["name"], customdata=trace["custom_data"],
            hovertemplate='%{y}%, %{customdata} schools, %{x}', offsetgroup=1,     marker=dict(color=colors[i])  # Use the colors list here
)

    traces.sort(key=lambda x: sum(x["y"]), reverse=True)

    # Calculate the total for each state
    survey_total = [sum(x) for x in zip(survey_1, survey_2, survey_3)]

    # Create the trace for the total

    # Create the figure and add the traces
    # Note: The total trace should be added first so that it's behind the other bars
    year = dashboard_filters['survey_taken_year']
    print('YEAR',year)
    # years_str = ', '.join(map(str, year))  # convert the array to a string
    # years_minus_2008 = [int(year1) - 2008 for year1 in year]  # subtract 2008 from each year
    # formatted_year_str = ', '.join(map(str, years_minus_2008))
    # print('YEAR1',formatted_year_str)
    # print('YEAR2',years_minus_2008)
    # Create the layout for the plot
    layout = dict(
        title='Year {0} ({1}) State Program response rate compared by School Level'.format(int(year)-2008,(str(int(year)-1)+'-'+str(year)[-2:])),
        yaxis=dict(range=[0, 100]),
        barmode='group',
    )

    # Create the figure and add the traces
    fig = go.Figure(data=[trace["trace"] for trace in traces], layout=layout)

    # Update the figure layout
    fig.update_layout(width=1400, height=500)

    # Generate the plot
    plot_div = plot(fig, output_type='div', include_plotlyjs=False)

    return plot_div

def school_survey_locale_level(dashboard_filters, isAdmin = False):

    school_surveys = school_suvery_locale_data(dashboard_filters, isAdmin)
    # print("school survey", school_surveys)
    data_json={}
    # if 'school_state__in' in data_json.keys():
    #     for val in school_surveys:
    #         if val['school_state__in'] not in data_json.keys():
    #             data_json[val['school_state__in']] = {}
    #         #data_json[val['school_state']][val['survey_taken']] = 0
    #         data_json[val['school_state__in']][str(val['survey_taken__in'])]=val['total']
    # else:
    totals = {}
    data_json_value = {}

    for val in school_surveys:
        if val['school_state'] not in data_json.keys():
            data_json[val['school_state']] = {}
            data_json_value[val['school_state']] = {}

        if str(val['survey_taken']) not in data_json[val['school_state']].keys():
            data_json[val['school_state']][str(val['survey_taken'])] = {}
            data_json_value[val['school_state']][str(val['survey_taken'])] = {}

            totals[(val['school_state'], str(val['survey_taken']))] = 0

        data_json[val['school_state']][str(val['survey_taken'])][val['grouped_locale']] = val['total']
        data_json_value[val['school_state']][str(val['survey_taken'])][val['grouped_locale']] = val['total']
        totals[(val['school_state'], str(val['survey_taken']))] += val['total']

    # Convert to percentages
    for state, surveys in data_json.items():
        for survey, locales in surveys.items():
            for locale, total in locales.items():
                data_json_value[state][survey][locale] = total 
                data_json[state][survey][locale] = round((total / totals[(state, survey)]) * 100, 0)
    
    school_state = list(data_json.keys())
        # school_state =(list(data_json.keys()))[0]

    # print("school_state", school_state, dashboard_filters, data_json)
    #convert to percentages
    # Initialize lists to store the data for each group
    survey_1 = []
    survey_2 = []
    survey_3 = []
    survey_4 = []
    survey_none = []
    survey_1_value = []
    survey_2_value = []
    survey_3_value = [] 
    survey_4_value = [] 

    # Iterate over each state
    for state in school_state:
        # Get the data for each group, or default to 0 if the group doesn't exist
        survey_1.append(data_json[state].get('True', {}).get('City', 0))
        survey_2.append(data_json[state].get('True', {}).get('Rural', 0))
        survey_3.append(data_json[state].get('True', {}).get('Suburb', 0))
        survey_4.append(data_json[state].get('True', {}).get('Town', 0))
        survey_1_value.append(data_json_value[state].get('True', {}).get('City', 0))
        survey_2_value.append(data_json_value[state].get('True', {}).get('Rural', 0))
        survey_3_value.append(data_json_value[state].get('True', {}).get('Suburb', 0))
        survey_4_value.append(data_json_value[state].get('True', {}).get('Town', 0))
        # survey_none.append(data_json[state].get('False', {}).get(None, 0))

    # Create the traces for the plot
    # trace_1 = go.Bar(x=school_state, y=survey_1, name='Emerging (Yes)')
    # trace_2 = go.Bar(x=school_state, y=survey_2, name='Developing (Yes)')
    # trace_3 = go.Bar(x=school_state, y=survey_3, name='Full Implementation (Yes)')
    # trace_none = go.Bar(x=school_state, y=survey_none, name='None')

    traces = [
    {"x": school_state, "y": [round(val) for val in survey_1], "name": 'City', "trace": None, "custom_data": survey_1_value},
    {"x": school_state, "y": [round(val) for val in survey_2], "name": 'Rural', "trace": None, "custom_data": survey_2_value},
    {"x": school_state, "y": [round(val) for val in survey_3], "name": 'Suburb', "trace": None, "custom_data": survey_3_value},
    {"x": school_state, "y": [round(val) for val in survey_4], "name": 'Town', "trace": None, "custom_data": survey_4_value}
]

    # Sort the traces based on their total values
    colors = ['rgba(200, 200, 220, 0.8)', 'rgba(168, 184, 134, 0.8)', 'rgba(170, 180, 200, 0.8)', 'rgba(109, 154, 168, 0.8)', 'rgba(120, 130, 160, 0.8)', 'rgba(140, 138, 173, 0.8)']     # Define your colors here with opacity

    # Create the actual traces
    for i, trace in enumerate(traces):
        trace["trace"] = go.Bar(x=trace["x"], y=trace["y"], name=trace["name"], customdata=trace["custom_data"],
            hovertemplate='%{y}%, %{customdata} schools, %{x}', offsetgroup=1,     marker=dict(color=colors[i])  # Use the colors list here
)


    # Create the trace for the total
    traces.sort(key=lambda x: sum(x["y"]), reverse=True)

    # Create the figure and add the traces
    # Note: The total trace should be added first so that it's behind the other bars
    year = dashboard_filters['survey_taken_year']
    # print('YEAR',year)
    # years_str = ', '.join(map(str, year))  # convert the array to a string
    # years_minus_2008 = [int(year1) - 2008 for year1 in year]  # subtract 2008 from each year
    # formatted_year_str = ', '.join(map(str, years_minus_2008))
    # print('YEAR1',formatted_year_str)
    # print('YEAR2',years_minus_2008)
    # Create the layout for the plot
    layout = dict(
        title='Year {0} ({1}) State Program response rate compared by Locale'.format(int(year)-2008,(str(int(year)-1)+'-'+str(year)[-2:])),
        yaxis=dict(range=[0, 100]),
        barmode='group',
    )

    # Create the figure and add the traces
    fig = go.Figure(data=[trace["trace"] for trace in traces], layout=layout)

    # Update the figure layout
    fig.update_layout(width=1400, height=500)

    # Generate the plot
    plot_div = plot(fig, output_type='div', include_plotlyjs=False)

    return plot_div

def school_survey_implementation_level(dashboard_filters, isAdmin = False):

    school_surveys = school_suvery_implementation_level_data(dashboard_filters, isAdmin)
    print("school survey", school_surveys)
    # Assuming data_json is your data
    # for state in states:
    # # Filter data for current state and survey_taken=True
    # state_data = [data for data in survey_data if data['school_state'] == state and data['survey_taken']]

    # # Get total for each implementation level and append to respective list
    # level_1_totals.append(sum(data['total'] for data in state_data if data['implementation_level'] == '1'))
    # level_2_totals.append(sum(data['total'] for data in state_data if data['implementation_level'] == '2'))
    # level_3_totals.append(sum(data['total'] for data in state_data if data['implementation_level'] == '3'))
    data_json={}
    # if 'school_state__in' in data_json.keys():
    #     for val in school_surveys:
    #         if val['school_state__in'] not in data_json.keys():
    #             data_json[val['school_state__in']] = {}
    #         #data_json[val['school_state']][val['survey_taken']] = 0
    #         data_json[val['school_state__in']][str(val['survey_taken__in'])]=val['total']
    # else:
    totals = {}
    data_json_value = {}
    for val in school_surveys:
        if val['school_state'] not in data_json.keys():
            data_json[val['school_state']] = {}
            data_json_value[val['school_state']] = {}
        if str(val['survey_taken']) not in data_json[val['school_state']].keys():
            data_json[val['school_state']][str(val['survey_taken'])] = {}
            data_json_value[val['school_state']][str(val['survey_taken'])] = {}

            totals[(val['school_state'], str(val['survey_taken']))] = 0

        data_json[val['school_state']][str(val['survey_taken'])][val['implementation_level']] = val['total']
        data_json_value[val['school_state']][str(val['survey_taken'])][val['implementation_level']] = val['total']
        totals[(val['school_state'], str(val['survey_taken']))] += val['total']

    # Convert to percentages
    for state, surveys in data_json.items():
        for survey, levels in surveys.items():
            for level, total in levels.items():
                data_json_value[state][survey][level] = total

                data_json[state][survey][level] = round((total / totals[(state, survey)]) * 100, 0)
        # data_json_value = list(data_json_value.keys())
        school_state = list(data_json.keys())
            # school_state =(list(data_json.keys()))[0]

    print("school_state", school_state, dashboard_filters, data_json)
  
        # survey_true_val = [data_json[i].get('True',0) for i in school_state]

    #convert to percentages
    # Initialize lists to store the data for each group
    survey_1 = []
    survey_2 = []
    survey_3 = []
    survey_1_value = []
    survey_2_value = []
    survey_3_value = []

    survey_none = []

    # Iterate over each state
    for state in school_state:
        # Get the data for each group, or default to 0 if the group doesn't exist
        survey_1.append(data_json[state].get('True', {}).get('1', 0))
        survey_2.append(data_json[state].get('True', {}).get('2', 0))
        survey_3.append(data_json[state].get('True', {}).get('3', 0))
        # survey_none.append(data_json[state].get('False', {}).get(None, 0))
        survey_1_value.append(data_json_value[state].get('True', {}).get('1', 0))
        survey_2_value.append(data_json_value[state].get('True', {}).get('2', 0))
        survey_3_value.append(data_json_value[state].get('True', {}).get('3', 0))


    # Create the traces for the plot
    # trace_1 = go.Bar(x=school_state, y=survey_1, name='Emerging (Yes)')
    # trace_2 = go.Bar(x=school_state, y=survey_2, name='Developing (Yes)')
    # trace_3 = go.Bar(x=school_state, y=survey_3, name='Full Implementation (Yes)')
    # trace_none = go.Bar(x=school_state, y=survey_none, name='None')

    traces = [
    {"x": school_state, "y": survey_1, "name": 'Emerging', "trace": None, "custom_data": survey_1_value},
    {"x": school_state, "y": survey_2, "name": 'Developing', "trace": None, "custom_data": survey_2_value},
    {"x": school_state, "y": survey_3, "name": 'Full Implementation', "trace": None, "custom_data": survey_3_value}
    ]

    # Sort the traces based on their total values
    traces.sort(key=lambda x: sum(x["y"]), reverse=True)
    # traces.reverse
    # colors = ['rgba(255, 0, 0, 1)', 'rgba(0, 255, 0, 1)', 'rgba(0, 0, 255, 1)']  # Define a list of colors

    # Create the actual traces
    colors = ['rgba(200, 200, 220, 0.8)', 'rgba(168, 184, 134, 0.8)', 'rgba(170, 180, 200, 0.8)', 'rgba(109, 154, 168, 0.8)', 'rgba(120, 130, 160, 0.8)', 'rgba(140, 138, 173, 0.8)']     # Define your colors here with opacity

    for i, trace in enumerate(traces):
        trace["trace"] = go.Bar(
            x=trace["x"], 
            y=trace["y"], 
            customdata=trace["custom_data"],
            hovertemplate='%{y}%, %{customdata} schools, %{x}',

            name=trace["name"],
            offsetgroup=1, 
            base=i*0.1,
            marker=dict(color=colors[i])  # Use the colors list here

            # width=0.5,
            # marker=dict(
            #     color=colors[i % len(colors)],  # Use the index to select a color
            #     opacity=1
            # )
        )

    # Calculate the total for each state
    survey_total = [sum(x) for x in zip(survey_1, survey_2, survey_3)]

    # Create the trace for the total

    # Create the figure and add the traces
    # Note: The total trace should be added first so that it's behind the other bars
    year = dashboard_filters['survey_taken_year']
    print('YEAR',year)
    # years_str = ', '.join(map(str, year))  # convert the array to a string
    # years_minus_2008 = [int(year1) - 2008 for year1 in year]  # subtract 2008 from each year
    # formatted_year_str = ', '.join(map(str, years_minus_2008))
    # print('YEAR1',formatted_year_str)
    # print('YEAR2',years_minus_2008)
    # Create the layout for the plot

    layout = dict(
        title='Year {0} ({1}) State Program response rate compared by Implementation Level'.format(int(year)-2008,(str(int(year)-1)+'-'+str(year)[-2:])),
        yaxis=dict(range=[0, 100]),
        barmode="group",
        bargap=0.1,  # Add this line
        
    )

    # Create the figure and add the traces
    fig = go.Figure(data=[trace["trace"] for trace in traces], layout=layout)

    # Update the figure layout
    fig.update_layout(width=1400, height=500)

    # Generate the plot
    plot_div = plot(fig, output_type='div', include_plotlyjs=False)

    return plot_div

def school_survey(dashboard_filters, isAdmin, getImage=False):

    school_surveys = school_suvery_data(dashboard_filters, isAdmin)
    # print("school survey", school_surveys)
    data_json={}
    # if 'school_state__in' in data_json.keys():
    #     for val in school_surveys:
    #         if val['school_state__in'] not in data_json.keys():
    #             data_json[val['school_state__in']] = {}
    #         #data_json[val['school_state']][val['survey_taken']] = 0
    #         data_json[val['school_state__in']][str(val['survey_taken__in'])]=val['total']
    # else:
    for val in school_surveys:
        if val['school_state'] not in data_json.keys():
            data_json[val['school_state']] = {}
            #data_json[val['school_state']][val['survey_taken']] = 0
        data_json[val['school_state']][str(val['survey_taken'])]=val['total']
   
    school_state = list(data_json.keys())
        # school_state =(list(data_json.keys()))[0]

    # print("school_state", school_state, dashboard_filters, data_json)

    survey_true_val = [data_json[i].get('True',0) for i in school_state]

    #convert to percentages
    for state in school_state:
        # print(state)
        total = data_json[state].get('True',0) + data_json[state].get('False',0)
        print("HERE IS THE TOTAL", total)
        data_json[state]['True'] = round((data_json[state].get('True',0)/total)*100,2)
        data_json[state]['False'] = round((data_json[state].get('False',0)/total)*100,2)

    survey_true = [data_json[i].get('True',0) for i in school_state]
    survey_false =[data_json[i].get('False',0) for i in school_state]
    print("survey_true", survey_true)
    survey_true = [round(value) for value in survey_true]
    trace = [go.Bar(
        x= school_state,
        y = survey_true,
        customdata=survey_true_val,
        hovertemplate='%{y}%, %{customdata} schools, %{x}',
        name='',
        marker=dict(color='rgba(109, 154, 168, 0.8)'))]
    year = dashboard_filters['survey_taken_year']
    # print('YEAR',year)
    years_str = year  # convert the array to a string
    # years_minus_2008 = [int(year1) - 2008 for year1 in year]  # subtract 2008 from each year
    # formatted_year_str = years_minus_2008
    # print('YEAR1',formatted_year_str)
    # print('YEAR2',years_minus_2008)

    # if isinstance(year, list):
        # year = year[0]    
    layout = dict(
        title='Year {0} ({1}) State Program response rate'.format(int(year)-2008,(str(int(year)-1)+'-'+str(year)[-2:])),
        yaxis = dict(
        title="Percentage Value (%)",
        range=[0, 100]),
        barmode='group',
    )

    fig = go.Figure(data=trace, layout=layout)
    fig.update_layout(width=1400, height=500)
    plot_div = plot(fig, output_type='div', include_plotlyjs=False)
    if getImage:
        img_bytes = io.BytesIO()
        py.write_image(fig, img_bytes, format='png')
        img_bytes.seek(0)
        return img_bytes
    else:
        if survey_true:
            return plot_div
        else:
             return None
    
def school_survey_over_time(dashboard_filters, getImage = False):
    # print("core_experience_yearly filters", filters)
    raw_data = survey_response_year_data(dashboard_filters)
    print(raw_data, "===========RAW DATA==============")

    data = survey_response_year_percentage_data(raw_data.copy())
    # print("CORE_EXP_YEAR:",data)

    print(data, "===========data==============")

    # print("IMPLEVEL:",data)
    df = pd.DataFrame(data)
    print(df, "===========df==============")

    print('SURVEY YEAR',(df == 0).all())
    print("end")
    print(raw_data, "===========RAW DATA1==============")

    
    # fig = px.line(df, x=df['survey_year'], y=df['emerging'], labels={"survey_year":"year","emerging":"Implementation Level"})#color???
    fig = go.Figure()
    # hovertemplate='Year: %{x}<br>Emerging: %{y}%<br>Raw Data: %{customdata}<extra></extra>'
    fig.add_scatter(
        x=df['survey_year'],
        y=df['state'].round(0),
        name="{0} response".format(dashboard_filters['state_abv']),
        customdata=raw_data['state_yes'],
        hovertemplate=(
        "%{x}, %{y}%, %{customdata} schools"
         )  )  
    fig.add_scatter(x=df['survey_year'],y=df['national'], name="National response", visible='legendonly', customdata=raw_data['national_yes'],
        hovertemplate=(
        "%{x}, %{y}%, %{customdata} schools"
         ) )
    title_name = 'Survey response rate over time,<br> National vs. {0} State Program'.format(dashboard_filters['state_abv'])

# for i in range(0,len(response['survey_year'])):
#             total=0
#             for val in ['emerging','developing','full_implement']:
#                 total += response[val][i]
#             for val in ['emerging','developing','full_implement']:
#                 # print(total)
#                 try:
#                     response[val][i]=round((response[val][i]/total)*100,2)
#                 except ZeroDivisionError:
#                     response[val][i]=0

#     for i in range(0,len(response['survey_year'])):
#             total=0
#             for val in ['state_emerging','state_developing','state_full_implement']:
#                 total += response[val][i]
#             for val in ['state_emerging','state_developing','state_full_implement']:
    fig.update_layout( 
    title={
        'text': title_name,
        # 'y': 0.95,  # Adjust the y position of the title (0 - bottom, 1 - top)
        # 'x': 0.5  # Adjust the x position of the title (0 - left, 0.5 - center, 1 - right)

        "x": 0.5,  # Adjust the x position of the title (0 - left, 0.5 - center, 1 - right)
        "y": 0.9,  # Adjust the y position of the title (0 - bottom, 1 - top)
        "yanchor": "top",  # Anchor point of the title (aligned to the top)

    },
    legend=dict(
        orientation="h",
    ),
    xaxis = dict (
        tickmode='linear',
        tick0 = min(df['survey_year']),
        dtick=1
    ),
     yaxis = dict (
        range=[0,100],
        title="Percentage value (%)",  # Add this line
    ),
    margin=dict(
        t=100
    ),

    )

    if getImage:
        img_bytes = io.BytesIO()
        py.write_image(fig, img_bytes, format='png')
        img_bytes.seek(0)
        return img_bytes
    else:
        plot_div = plot(fig, output_type='div', include_plotlyjs=False)
        # print("imp level yoo?")
        if (df == 0).all().all():
            return None
        return plot_div
import numpy as np

def core_experience(dashboard_filters, getImage = False):
    # survey_year=SchoolDetails.objects.aggregate(Max('survey_taken_year'))
    # survey_year = survey_year['survey_taken_year__max']
    # print("core experience")
    filters = filter_set(dashboard_filters)
    # print("after filter", filters)
    sports=core_experience_data(dashboard_filters,'sports',range='state')
    leadership = core_experience_data(dashboard_filters,'leadership',range='state')
    wholeschool = core_experience_data(dashboard_filters,'whole_school',range='state')

    # print(sports,leadership,wholeschool)
    # print("final filters:", filters)
    colors = ['rgba(170, 180, 200, 0.8)', 'rgba(109, 154, 168, 0.8)', 'rgba(120, 130, 160, 0.8)']  # Define your colors here with opacity
    core_exp_df = pd.DataFrame(dict(
        lables = ['Unified Sports','Inclusive Youth Leadership','Whole School Engagement'],
        values = [sports,leadership,wholeschool]
    ))

    print
    filters = add_in_forFilters(filters)
    fig = Figure(data=[Pie(labels=core_exp_df['lables'], 
                        values=core_exp_df['values'], 
                        hovertemplate='%{label}, %{value} schools<extra></extra>')])

    # Set the color of the pie chart
    fig.update_traces(marker=dict(colors=colors))

    # Set the title of the plot
    fig.update_layout(title_text='Core Experience implementation in {year} {state_abv}'.format(state_abv=filters['state_abv'],year=('('+str(int(filters['survey_taken_year'])-1)+'-'+str(filters['survey_taken_year'])[-2:]+')')))
    plot_div = plot(fig, output_type='div', include_plotlyjs=False)
    # print("plot div yo", plot_div)
    if getImage:
#         fig.update_layout(
#     autosize=True,
#     width=900,  # Adjust as needed
#     height=1024,  # Adjust as needed
# )
        img_bytes = io.BytesIO()
        py.write_image(fig, img_bytes, format='png')
        img_bytes.seek(0)
        return img_bytes
    else:
        if sports or leadership or wholeschool:
            return plot_div
        else:
            return None


def core_experience_yearly(dashboard_filters, getImage = False):
    filters = filter_set(dashboard_filters)
    raw_data = core_experience_year_raw_data(dashboard_filters)
    # print("core_experience_yearly filters", filters)
    data = core_experience_year_data(dashboard_filters)

    # print("CORE_EXP_YEAR:",data)

    #{'sports': [6370, 3461], 'leadership': [3914, 2560], 'whole_school': [5132, 3361], 'survey_year': [2021, 2022], 'state_sports': [47, 21], 'state_leadership': [18, 12], 'state_whole_school': [26, 18]}
    print(raw_data, "CORE EPEXRIENCE RAW DATA")
    df = pd.DataFrame(data)
    print("CORE EXP SURVEY YEAR",(df))
    fig = go.Figure()
    fig.add_scatter(x=df['survey_year'],y=df['state_leadership'].round(0), customdata=raw_data['state_leadership'],
        hovertemplate=(
        "%{x}, %{y}%, %{customdata} schools"
         ), name="{state} Inclusive Youth Leadership".format(state=filters['state_abv']))
    fig.add_scatter(x=df['survey_year'],y=df['state_sports'].round(0), customdata=raw_data['state_sports'],
        hovertemplate=(
        "%{x}, %{y}%, %{customdata} schools"
         ), name="{state} Unified Sports".format(state=filters['state_abv']))
    fig.add_scatter(x=df['survey_year'],y=df['state_whole_school'].round(0), customdata=raw_data['state_whole_school'],
        hovertemplate=(
        "%{x}, %{y}%, %{customdata} schools"
         ), name="{state} School Engagement".format(state=filters['state_abv']))

    fig.add_scatter(x=df['survey_year'],y=df['sports'].round(0), customdata=raw_data['sports'],
        hovertemplate=(
        "%{x}, %{y}%, %{customdata} schools"
         ), name="Unified Sports (National)",  visible='legendonly' )
    fig.add_scatter(x=df['survey_year'],y=df['whole_school'].round(0),customdata=raw_data['whole_school'],
        hovertemplate=(
        "%{x}, %{y}%, %{customdata} schools"
         ),  name="Whole School Engagement (National)",  visible='legendonly')
    fig.add_scatter(x=df['survey_year'],y=df['leadership'].round(0), customdata=raw_data['leadership'],
        hovertemplate=(
        "%{x}, %{y}%, %{customdata} schools"
         ), name="Inclusive Youth Leadership (National)",  visible='legendonly')
    title_name = "Percentage of Core experience implementation over time,<br> National vs {0} State program <br><br>".format(filters['state_abv'])
    
    fig.update_layout( 
        
    title={
        'text': title_name,
        # 'y': 0.95,  # Adjust the y position of the title (0 - bottom, 1 - top)
        # 'x': 0.5,  # Adjust the x position of the title (0 - left, 0.5 - center, 1 - right)
         "x": 0.5,  # Adjust the x position of the title (0 - left, 0.5 - center, 1 - right)
        "y": 0.9,  # Adjust the y position of the title (0 - bottom, 1 - top)
        "yanchor": "top",  # Anchor point of the title (aligned to the top)
        # "font": {"size": 20},  # Font size of the title
        # "pad": {"t": 5}  
    },
    legend=dict(
        orientation="h",
    ),
    xaxis = dict (
        tickmode='linear',
        tick0 = min(df['survey_year']),
        dtick=1
    ),
    yaxis = dict (
        range=[0,100],
        title="Percentage value (%)",  # Add this line
    ),
      margin=dict(
        t=100  # Increase the top margin (adjust the value as needed)
    )
      )
    
    if getImage:
        img_bytes = io.BytesIO()
        py.write_image(fig, img_bytes, format='png')
        img_bytes.seek(0)
        return img_bytes
    else:
        plot_div = plot(fig, output_type='div', include_plotlyjs=False)
        if (df.drop('survey_year', axis=1) == 0.0).all().all():
            return None
        return plot_div


def load_dashboard(dashboard_filters,dropdown,isAdmin=False, getImage = False):
        # print("This is it", dashboard_filters, dropdown)
        plot1 = school_survey(dashboard_filters, isAdmin, getImage=getImage)
        plot2 = core_experience(dashboard_filters, getImage=getImage)
        plot3 = implementation_level(dashboard_filters, getImage=getImage)
        plot4 = core_experience_yearly(dashboard_filters, getImage=getImage)
        plot5 = implement_unified_sport_activity(dashboard_filters, getImage=getImage)
        plot6 = implement_youth_leadership_activity(dashboard_filters, getImage=getImage)
        plot7 = implement_school_engagement_activity(dashboard_filters, getImage=getImage)
        plot8 = sona_resources_useful(dashboard_filters, getImage=getImage)
        plot9 = school_survey_over_time(dashboard_filters, getImage=getImage)

        context={
            # 'plot1':school_survey(dashboard_filters),
            # 'plot2':core_experience(dashboard_filters),
            # 'plot3':implementation_level(dashboard_filters),
            # 'plot4':core_experience_yearly(dashboard_filters),
            # 'plot5':implement_unified_sport_activity(dashboard_filters),
            # 'plot6':implement_youth_leadership_activity(dashboard_filters),
            # 'plot7':implement_school_engagement_activity(dashboard_filters),
            # 'plot8':sona_resources_useful(dashboard_filters),
            'form':dropdown,
            'plot_titles': {
            'plot1': "State Program response rate",
            'plot2': "Core Experience implementation",
            'plot3': "Implementation level over time",
            'plot4': "Percentage of Core experience implementation over time",
            'plot5': "Percentage of schools implementing each Unified Sports activity",
            'plot6': "Percentage of schools implementing each Inclusive Youth Leadership activity",
            'plot7': "Percentage of schools implementing each Whole School Engagement activity",
            'plot8': "Percentage of liaisons who found SONA resources useful",
            'plot9': "Survey response rate over time",

        }
        }
        
        if plot1 is not None:
            context['plot1'] = plot1
        if plot2 is not None:
            context['plot2'] = plot2
        if plot3 is not None:
            context['plot3'] = plot3
        if plot4 is not None:
          context['plot4'] = plot4
        if plot5 is not None:
            context['plot5'] = plot5
        if plot6 is not None:
            context['plot6'] = plot6
        if plot7 is not None:
            context['plot7'] = plot7
        if plot8 is not None:
            context['plot8'] = plot8
        if plot9 is not None:
            context['plot9'] = plot9
        return context



@login_required(login_url='../auth/login/')
def index(request):
    state = CustomUser.objects.values('state').filter(username=request.user)[0]
    state=state.get('state','None')
    admin = False
    if request.method=='GET':
        filter_state = state
        if state=='all':
            filter_state = 'AK'# on inital load some data has to be displayed so defaulting to ma
            admin = True
        context = load_dashboard(dashboard_filters={'state_abv': filter_state,'survey_taken_year': '2022'},dropdown=Filters(state=state_choices(state)), isAdmin=admin)
    
    if request.method=='POST':
        print(request)
        getState = CustomUser.objects.values('state').filter(username=request.user)[0]
        getState=getState.get('state','None')
        admin = False
        if getState == 'all':
            admin = True

        state = state_choices(state)
        post_data = request.POST.copy()  # Make a mutable copy of the POST data
        # if not isinstance(post_data.get('school_county'), str):
        dropdown = Filters(state,post_data)
        if not dropdown.is_valid():
            post_data['school_county'] = 'all'
            dropdown = Filters(state,post_data)



        # if not isinstance(dropdown.cleaned_data.get('school_county'), str):
        #         dropdown.cleaned_data['school_county'] = 'all'
        print("===================",dropdown)
        print("==State==", dropdown.is_valid())
        if not dropdown.is_valid():
            print(dropdown.errors)

        if dropdown.is_valid():
            #print('heloooooo')
            dashboard_filters = dropdown.cleaned_data
            print("==State==", dashboard_filters)

            # print("@@@@@@@@@@@@", dashboard_filters)
            context = load_dashboard(dashboard_filters,dropdown, isAdmin=admin)

                        # Create a new PDF in memory
            
    # cache.set('context', context, 300)  # Cache the context for 300 seconds

    return render(request, 'analytics/index_graph.html', context) 
         

def get_graph(request):
    # print("REQUEST CHECK", request)
    state = CustomUser.objects.values('state').filter(username=request.user)[0]
    state=state.get('state','None')
    print(state)
    dashboard_filters = request.GET.copy()  # Get the filters from the request
    type = dashboard_filters['type']
    graph_no = dashboard_filters['graph_no'][0]
    admin = False
    # print(dashboard_filters)
    dashboard_filters.pop('type')
    dashboard_filters.pop('graph_no')
    if state=='all':
        admin = True
    # print("NEW FUNCTION:", dashboard_filters, type, graph_no)
    if graph_no is '1':
        # print("NEW FUNCTION2:", graph_no)
        match type:
            case 'locale':
                plot_div = school_survey_locale_level(dashboard_filters, isAdmin = admin)
            case 'imp_level':
                plot_div = school_survey_implementation_level(dashboard_filters, isAdmin = admin)
            case 'school_level':
                plot_div = school_survey_school_level(dashboard_filters, isAdmin = admin)
            case 'survey_taken_year':
                plot_div = school_survey_year(dashboard_filters, isAdmin = admin)
            case 'reset':
                print("RESET BEING USED")
                plot_div = school_survey(dashboard_filters, isAdmin = admin)
            case '':
                plot_div = school_survey(dashboard_filters, isAdmin = admin)
    elif graph_no is '5':
            if type == 'reset':
                plot_div = implement_unified_sport_activity(dashboard_filters=dashboard_filters, type="default")

            else:    
                plot_div = implement_unified_sport_activity(dashboard_filters=dashboard_filters, type=type)
    elif graph_no is '6':
            if type == 'reset':
                plot_div = implement_youth_leadership_activity(dashboard_filters=dashboard_filters, type="default")

            else:    
                plot_div = implement_youth_leadership_activity(dashboard_filters=dashboard_filters, type=type)

    elif graph_no is '7':
            if type == 'reset':
                plot_div = implement_school_engagement_activity(dashboard_filters=dashboard_filters, type="default")

            else:    
                plot_div = implement_school_engagement_activity(dashboard_filters=dashboard_filters, type=type)
    elif graph_no is '8':
            if type == 'reset':
                plot_div = sona_resources_useful(dashboard_filters=dashboard_filters, type='default')
            else:
                plot_div = sona_resources_useful(dashboard_filters=dashboard_filters, type=type)
 
    
    # plot_div = school_survey_implementation_level(dashboard_filters)
    # print("YOO NEW DATA", plot_div)
    return JsonResponse({'plot_div': mark_safe(plot_div)})
     

def get_counties(request):
    state_abv = request.GET.get('state_abv')
    counties = SchoolDetails.objects.filter(state_abv=state_abv).values_list('school_county', flat=True)
    county_dict = {}
    county_dict.update({county: county for county in counties if county != '-99'})
    county_dict.update({'all': 'All'} ) 

    # print(county_dict)
    return JsonResponse(county_dict, safe=False)


def generate_pdf_file(request):

    state = CustomUser.objects.values('state').filter(username=request.user)[0]
    state=state.get('state','None')
    admin = False

    getState = CustomUser.objects.values('state').filter(username=request.user)[0]
    getState=getState.get('state','None')
    admin = False
    if getState == 'all':
        admin = True

    state = state_choices(state)
    post_data = request.POST.copy()  # Make a mutable copy of the POST data
    # if not isinstance(post_data.get('school_county'), str):
    dropdown = Filters(state,post_data)
    if not dropdown.is_valid():
        post_data['school_county'] = 'all'
        dropdown = Filters(state,post_data)



    # if not isinstance(dropdown.cleaned_data.get('school_county'), str):
    #         dropdown.cleaned_data['school_county'] = 'all'
    print("===================",dropdown)
    print("==State==", dropdown.is_valid())
    if not dropdown.is_valid():
        print(dropdown.errors)

    if dropdown.is_valid():
        #print('heloooooo')
        dashboard_filters = dropdown.cleaned_data
        print("==State==", dashboard_filters)

        # print("@@@@@@@@@@@@", dashboard_filters)
        context = load_dashboard(dashboard_filters,dropdown, isAdmin=admin, getImage=True)


    # context = load_dashboard(dashboard_filters={'state_abv': filter_state,'survey_taken_year': '2023'},dropdown=Filters(state=state_choices(state)), isAdmin=admin, getImage=True)
        print(dashboard_filters)
        buffer = BytesIO()
        c = canvas.Canvas(buffer)
        # c.drawString(100, 100, "Hello world.")
        print("CONTEXT", context)
        c.setFont("Helvetica-Bold", 18)  # Set the font and size
        c.drawCentredString(300, 800, "Special Olympics Report")  # Draw the title
        pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))

        # Adjust these as needed
        x = 50
        y = 250
        width = 400
        height = 200
        
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 760, "Filters Used")


        # Set the font and size
        # dashboard_filter = {'implementation_level': 'all', 'locale__startswith': 'all', 'gradeLevel_WithPreschool': 'all', 'survey_taken_year': '2022', 'state_abv': 'AK', 'school_county': 'all'}
                # Draw the text
        c.setFont("Helvetica-Bold", 12)

        # Draw the bold part of the text
        c.drawString(70, 730, "Implementation level - ")

        # Calculate the width of the bold text
        bold_text_width = stringWidth("Implementation level - ", "Helvetica-Bold", 12)

        # Set the font and size back to normal
        c.setFont("Helvetica", 12)

        # Draw the normal part of the text, starting after the bold text
        c.drawString(70 + bold_text_width, 730, f"{dashboard_filters['implementation_level'].capitalize()}")        # Set the font and size to bold
        c.setFont("Helvetica-Bold", 12)

        # Draw the bold part of the text and the normal part of the text for each line
        bold_text = "Locale - "
        c.drawString(70, 710, bold_text)
        c.setFont("Helvetica", 12)
        c.drawString(70 + stringWidth(bold_text, "Helvetica-Bold", 12), 710, f"{dashboard_filters['locale__startswith'].capitalize()}")

        c.setFont("Helvetica-Bold", 12)
        bold_text = "School Level - "
        c.drawString(70, 690, bold_text)
        c.setFont("Helvetica", 12)
        c.drawString(70 + stringWidth(bold_text, "Helvetica-Bold", 12), 690, f"{dashboard_filters['gradeLevel_WithPreschool'].capitalize()}")

        c.setFont("Helvetica-Bold", 12)
        bold_text = "Survey Year - "
        c.drawString(70, 670, bold_text)
        c.setFont("Helvetica", 12)
        c.drawString(70 + stringWidth(bold_text, "Helvetica-Bold", 12), 670, f"{dashboard_filters['survey_taken_year'].capitalize()}")

        c.setFont("Helvetica-Bold", 12)
        bold_text = "State program - "
        c.drawString(70, 650, bold_text)
        c.setFont("Helvetica", 12)
        c.drawString(70 + stringWidth(bold_text, "Helvetica-Bold", 12), 650, f"{dashboard_filters['state_abv']}")

        c.setFont("Helvetica-Bold", 12)
        bold_text = "County - "
        c.drawString(70, 630, bold_text)
        c.setFont("Helvetica", 12)
        c.drawString(70 + stringWidth(bold_text, "Helvetica-Bold", 12), 630, f"{dashboard_filters['school_county'].capitalize()}")


        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 580, "Graphs")
        # # Convert each Plotly graph to an image and embed it in the PDF
        if dashboard_filters['survey_taken_year'] == '2023':
            year = "15 (2022-23)"
        elif dashboard_filters['survey_taken_year'] == '2022':
            year = "14 (2021-22)"
        elif dashboard_filters['survey_taken_year'] == '2021':
            year = "13 (2020-21)"
        elif dashboard_filters['survey_taken_year'] == '2020':
            year = "12 (2019-20)"
        elif dashboard_filters['survey_taken_year'] == '2019':
            year = "11 (2018-19)"
        else:
            year = "Unknown Year"

        # for i in range(1, 10):  # Change this to range(1, 9) to include all graphs
            # print("GRAPH IMAGE", context[f'plot{i}'])
        # print("PLOT NUMBER:", i)
        if f'plot9' in context and context[f'plot9']:
            image = Image.open(io.BytesIO(context[f'plot9'].getvalue()))
      
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp:
                image.save(temp.name)
                c.setFont("Helvetica", 12)  # Set the font and size for the graph title
            
                c.drawString(70, 550, f"1. Survey response rate over time")  # Draw the graph title

                c.drawImage(temp.name, 70, 360, 320, 170)
                # y -= 200  # Move down for the next image

        if f'plot1' in context and context[f'plot1']:
            image = Image.open(io.BytesIO(context[f'plot1'].getvalue()))
      
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp:
                image.save(temp.name)
                c.drawString(70, 340, f"2. State program response rate")  # Draw the graph title                        c.drawString(x, y, f"State program response rate")  # Draw the graph title

                
                c.drawImage(temp.name, 70, 120, 480, 200)
                c.setFont("Helvetica", 8)  # Set the font and size for the graph title

                c.drawString(150, 110, f"This figure illustrates the response rates for the Year {year} State Program.")  # Draw the graph title

        #     y -= 240  # Move down for the next image

            c.showPage()

        if f'plot2' in context and context[f'plot2']:
            image = Image.open(io.BytesIO(context[f'plot2'].getvalue()))
      
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp:
                image.save(temp.name)
                c.setFont("Helvetica", 12)  # Set the font and size for the graph title

                c.drawString(70, 780, f"3. Core Experience Implementation")  # Draw the graph title                        c.drawString(x, y, f"State program response rate")  # Draw the graph title
                c.drawImage(temp.name, 70, 580, 330, 190)
                c.setFont("Helvetica", 8)  # Set the font and size for the graph title

                c.drawString(80, 570, f"The graph depicts the implementation of the Core Experience in {dashboard_filters['state_abv']}, categorized by sports, whole school, and leadership.")  # Draw the graph title

        if f'plot3' in context and context[f'plot3']:
            image = Image.open(io.BytesIO(context[f'plot3'].getvalue()))
      
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp:
                image.save(temp.name)
                c.setFont("Helvetica", 12)  # Set the font and size for the graph title

                c.drawString(70, 540, f"4. Implementation Level Over Time")  # Draw the graph title                        c.drawString(x, y, f"State program response rate")  # Draw the graph title
                c.drawImage(temp.name, 70, 320, 330, 190)
                c.setFont("Helvetica", 8)  # Set the font and size for the graph title

                c.drawString(90, 310, f"This figure illustrates the implementation levels over time for National vs {dashboard_filters['state_abv']} State Program,")
                c.drawString(90, 300, f"segmented into national and state emerging, developing, and full implementation.")  # Draw the graph title

                    

                    

                # elif i == 3:
                #                     c.drawImage(temp.name, x, y, 400, 180)

                # elif i == 4:
                #                     c.drawImage(temp.name, x, y, 500, 130)

                # elif i == 5:
                #                     c.drawImage(temp.name, x, y, 500, 130)

                # elif i == 6:
                #                     c.drawImage(temp.name, x, y, 500, 130)

                # elif i == 7:
                #                     c.drawImage(temp.name, x, y, 500, 130)

                # elif i == 8:
                #         c.drawImage(temp.name, x, y, 500, 130)

                

        c.showPage()
        c.save()

        buffer.seek(0)
        return buffer

def download_pdf(request):
   

    pdf = generate_pdf_file(request)
    return FileResponse(pdf, as_attachment=True, filename='report.pdf')
'''
Utility functions
'''

'''
input list or single dict 
return list of percent values or returns nested dict with value and percent
op sample :'state': {None: {'value': 0, 'percent_val': 0.0}, 'Yes': {'value': 4, 'percent_val': 7.0}, 'No': {'value': 53, 'percent_val': 93.0}}}
'''
def percentage_values(total_values, column_name = "", compare_type = "default"):
    print("percentage_values", column_name, total_values, compare_type)
    if type(total_values) == list:
        values = total_values
        return [round(((i/sum(values))*100),2) for i in values]
    elif type(total_values) == dict:
        data = list(total_values.values())
        try:
            percent_arr=[round(((i/sum(data))*100),1) for i in data ] 
        except ZeroDivisionError:
            percent_arr = [0]*len(data)
        res = {key:{'value':total_values[key],'percent_val':percent_arr[i]} for i,key in enumerate(total_values.keys()) }
        return res
    elif isinstance(total_values, QuerySet):
        result = {}
        sum_of_totals = sum(item['total'] for item in total_values)
        for item in total_values:
            column_name_val = item[column_name]
            if column_name_val not in result:
                result[column_name_val] = []
            percentage = round((item['total'] / sum_of_totals) * 100, 2) if sum_of_totals != 0 else 0
            match compare_type:
                case 'imp_level':
                    result[column_name_val].append({'implementation_level': item['implementation_level'], 'total': item['total'], 'percentage': percentage})
                case 'locale':
                    result[column_name_val].append({'grouped_locale': item['grouped_locale'], 'total': item['total'], 'percentage': percentage})
                case 'school_level':
                    result[column_name_val].append({'gradeLevel_WithPreschool': item['gradeLevel_WithPreschool'], 'total': item['total'], 'percentage': percentage})
                case 'survey_taken_year':
                    print(result)
                    result[column_name_val].append({'survey_taken_year': item['survey_taken_year'], 'total': item['total'], 'percentage': percentage})
                    print(result[column_name_val])
                    print("WORKING!!")

        # print("the new result", result)
        return result
    
def state_choices(state):#used for drop down in filters
    STATE_CHOICES = []
    STATE_CHOICES_RAW= list(SchoolDetails.objects.values_list('state_abv','school_state').distinct())
    if state =='all' or state== STATE_CHOICES_RAW:
        for val in STATE_CHOICES_RAW:
            if val[0]!='-99':
                STATE_CHOICES.append(val)
                STATE_CHOICES.sort()
        return STATE_CHOICES
    else:
        for val in STATE_CHOICES_RAW:
            if val[0]==state:
                return [(val[0],val[1])]
    return None
'''
query function for below six graphs
as pattern is same only column names are changing i used this method for fetching data
#none/null values are by default counted as o in this query
op sample:# {'sports_sports_teams': {'national': {'No': 2094, None: 0, 'Yes': 2033}, 'state': {None: 0, 'No': 24, 'Yes': 33}}, 'sports_unified_PE': {'national': {'No': 1945, None: 0, 'Yes': 2182}, 'state': {None: 0, 'No': 22, 'Yes': 35}}, 'sports_unified_fitness': {'national': {'No': 3292, None: 0, 'Yes': 835}, 'state': {None: 0, 'No': 44, 'Yes': 13}}, 'sports_unified_esports': {'national': {'No': 3903, None: 0, 'Yes': 224}, 'state': {None: 0, 'Yes': 4, 'No': 53}}, 'sports_young_athletes': {'national': {'No': 3450, None: 0, 'Yes': 677}, 'state': {None: 0, 'No': 46, 'Yes': 11}}, 'sports_unified_developmental_sports': {'national': {'No': 3505, None: 0, 'Yes': 622}, 'state': {None: 0, 'No': 49, 'Yes': 8}}}

'''
def main_query(column_name,filters,key,compareType="default"): 
    print("FILTERS NEW:", filters, column_name)
    if key=='state':
        filters=filters
    if key=='all':
        filters=filters.copy()
        if 'state_abv' in filters:
            filters.pop('state_abv')
        if 'state_abv__in' in filters:
            filters.pop('state_abv__in')
        if 'county' in filters:
            filters.pop('county')

        
    # print("Main_QUery_filters", compareType, filters)
    # print("Filters wow", filters)

    data = {}
    match compareType:
        case "default":
            data = dict(SchoolDetails.objects.values_list(column_name).filter(**filters).annotate(total = Count(column_name)))
        case "imp_level":
            data = (SchoolDetails.objects.values(column_name, "implementation_level").filter(**filters).annotate(total = Count(column_name)))
        case "locale":
            data = (SchoolDetails.objects.values(column_name).filter(**filters).annotate(total = Count(column_name)))

            # data = dict(SchoolDetails.objects.values_list(column_name, "locale").filter(**filters).annotate(total = Count(column_name)))
            data = data.annotate(
             grouped_locale=Case(
            When(locale__startswith='City', then=Value('City')),
            When(locale__startswith='Rural', then=Value('Rural')),
            When(locale__startswith='Suburb', then=Value('Suburb')),
            When(locale__startswith='Town', then=Value('Town')),
            default=Value('Other'),
            output_field=CharField(),
            )
            )
            data = data.values(column_name, "grouped_locale").annotate(total = Count(column_name))

        case "school_level":
            data = (SchoolDetails.objects.values(column_name, "gradeLevel_WithPreschool").filter(**filters).annotate(total = Count(column_name)))
        case "survey_taken_year":

            filters.pop('survey_taken_year',None)

    
    # print(filters)
    
    #  SchoolDetails.objects.values('school_state','survey_taken', 'survey_taken_year').filter(**filters).exclude(school_state='-99').annotate(total = Count('survey_taken')).order_by('school_state')
            data = (SchoolDetails.objects.values(column_name, "survey_taken_year").filter(**filters).annotate(total = Count(column_name)))
            # print("RESULT DATA:", data)
    
    print("MAIN QUERY PRINT", compareType, data)
    #test query to run in terminal: dict(SchoolDetails.objects.values_list('sports_sports_teams').filter(state_abv='sca',survey_taken_year=2022).annotate(total = Count('sports_sports_teams')))
    return data




'''
LOGIC
'''
def implement_unified_sport_activity(dashboard_filters, type="default", getImage = False):
    response={'sports_sports_teams':{}, 'sports_unified_PE':{},'sports_unified_fitness':{},
             'sports_unified_esports':{},'sports_young_athletes':{},'sports_unified_developmental_sports':{}}
    filters=filter_set(dashboard_filters)
    # print("implement_unified_sport_activity filters", filters)
    filters = add_in_forFilters(filters)

    comparedBy = ""
    match type:
        case 'imp_level':
            comparedBy = "compared by Implementation Level"
        case 'locale':
            comparedBy = "compared by Locale"
        case 'school_level':
            comparedBy = "compared by School Level"
        case 'survey_taken_year':
            comparedBy = "compared by Survey Year" 
    for column_name in response.keys():
        response[column_name]['national']=percentage_values(main_query(column_name,filters,key='all')) 
        response[column_name]['state']=percentage_values(main_query(column_name,filters,key='state', compareType=type), column_name, compare_type=type)
    y_axis = ['Unified Sports Teams', 'Unified PE', 'Unified fitness','Unified esports', 'Young athletes(participants)', 'Unified Developmental Sports']
    title='Percentage of schools implementing each <br> Unified Sports activity in {0} vs. National data {1}'.format(dashboard_filters['state_abv'], comparedBy)
    state=dashboard_filters['state_abv']#adding state to the response for graph lables
    emptyGraph = True
    print("implement_unified_sport_activity state", response)

    for column_name in response.keys():
        if response[column_name]['state']:
            print("Found state", response[column_name]['state'])
            emptyGraph = False
    print("SOMETHING!!!!", emptyGraph)
    if emptyGraph:
        return None
    else:
        return horizontal_bar_graph(response,y_axis,title,state,compare_type=type,getImage=getImage)
    
    


def implement_youth_leadership_activity(dashboard_filters, type="default", getImage = False):
    response = {'leadership_unified_inclusive_club':{},'leadership_youth_training':{},'leadership_athletes_volunteer':{},
               'leadership_youth_summit':{},'leadership_activation_committe':{}}
    filters=filter_set(dashboard_filters)
    filters = add_in_forFilters(filters)
    print("===========THE TYPE:", type)
    comparedBy = ""
    match type:
        case 'imp_level':
            comparedBy = "compared by Implementation Level"
        case 'locale':
            comparedBy = "compared by Locale"
        case 'school_level':
            comparedBy = "compared by School Level"
        case 'survey_taken_year':
            comparedBy = "compared by Survey Year"   
    
    for column_name in response.keys():
        response[column_name]['national']=percentage_values(main_query(column_name,filters,key='all')) 
        response[column_name]['state']=percentage_values(main_query(column_name,filters,key='state', compareType=type), column_name, compare_type=type)
    y_axis=['Unifed/Inclusive Club','Inclusive Youth Leadership Training/Class','Young Athletes Volunteers','Youth summit','Youth Activation Committee']
    title='Percentage of schools implementing each <br>  Youth Leadership activity in Program {0} vs. National data {1}'.format(dashboard_filters['state_abv'], comparedBy)
    state=dashboard_filters['state_abv']#adding state to the response for graph lables
    
    
    emptyGraph = True
    print("implement_unified_sport_activity state", response)

    for column_name in response.keys():
        if response[column_name]['state']:
            print("Found state", response[column_name]['state'])
            emptyGraph = False

    if emptyGraph:
        return None
    else:
        return horizontal_bar_graph(response,y_axis,title,state,compare_type=type, getImage= getImage)
    
    # return horizontal_bar_graph(response,y_axis,title,state,compare_type=type)

    


def implement_school_engagement_activity(dashboard_filters, type="default", getImage = False):
    response = {'engagement_spread_word_campaign':{},'engagement_fansinstands':{},'engagement_sports_day':{},
                'engagement_fundraisingevent':{},'engagement_SO_play':{},'engagement_fitness_challenge':{}}
    
    filters=filter_set(dashboard_filters)
    filters = add_in_forFilters(filters)
    comparedBy = ""
    match type:
        case 'imp_level':
            comparedBy = "compared by Implementation Level"
        case 'locale':
            comparedBy = "compared by Locale"
        case 'school_level':
            comparedBy = "compared by School Level"
        case 'survey_taken_year':
            comparedBy = "compared by Survey Year" 
    for column_name in response.keys():
        response[column_name]['national']=percentage_values(main_query(column_name,filters,key='all',)) 
        response[column_name]['state']=percentage_values(main_query(column_name,filters,key='state',compareType=type), column_name, compare_type=type)
    y_axis=['Spread the word'+'<br>'+'Inclusion/Respect/Disability' +'<br>'+'Awareness Campaign','Unified Sports pep Rally','Unified Sports Day/Festival','Fundraising events /activities','Special Olympics play/performance','Unified Fitness Challenge']
    # print("STATE ABV CHECK", dashboard_filters['state_abv'])
    title='Percentage of schools implementing each <br> Inclusive Whole School Engagement activity in Program {0} vs. National Data {1}'.format(dashboard_filters['state_abv'], comparedBy)
    state=dashboard_filters['state_abv']#adding state to the response for graph lables
    emptyGraph = True
    print("implement_unified_sport_activity state", response)

    for column_name in response.keys():
        if response[column_name]['state']:
            print("Found state", response[column_name]['state'])
            emptyGraph = False

    if emptyGraph:
        return None
    else:
        return horizontal_bar_graph(response,y_axis,title,state,compare_type=type, getImage = getImage)
    
    # return horizontal_bar_graph(response,y_axis,title,state,compare_type=type)


def sona_resources_useful(dashboard_filters, type="default", getImage = False):
    response={'elementary_school_playbook':{},'middle_level_playbook':{},'high_school_playbook':{},'special_olympics_state_playbook':{},'special_olympics_fitness_guide_for_schools':{},'unified_physical_education_resource':{},
              'special_olympics_young_athletes_activity_guide':{},'inclusive_youth_leadership_training_faciliatator_guide':{},'planning_and_hosting_a_youth_leadership_experience':{},'unified_classoom_lessons_and_activities':{},'generation_unified_youtube_channel_or_videos':{},'inclusion_tiles_game_or_facilitator_guide':{}}
    column_names=response.keys()
    filters=filter_set(dashboard_filters)
    filters = add_in_forFilters(filters)
    # print("sona", filters)
    for column_name in response.keys():
        response[column_name]['national']=percentage_values(main_query(column_name,filters,key='all')) 
        response[column_name]['state']=percentage_values(main_query(column_name,filters,key='state',compareType=type), column_name, compare_type=type)
    # state=dashboard_filters['state_abv']#adding state to the response for graph lables
    ##seperating yes and no keys from each parent key
    # print("sona 1", response, type)
    state_no=[]
    nation_no=[]
    state_yes=[]
    nation_yes=[]
    state_yes_val=[]
    state_no_val=[]
    nation_yes_val=[]
    if type == "default":
        for val in column_names:
            n_keys=response[val]['national'].keys()
            s_keys=response[val]['state'].keys()
            for key in n_keys:
                if key=='1':
                    # nation_no.append(response[val]['national'].get(key,{}).get('percent_val',0))
                # elif key!=None and key!='0': 
                    #logic here is the response has only three keys for all columns so if its not these two then it should be the column name
                    #saves time to avoid writing down all column yes names and then verifying
                    nation_yes.append(response[val]['national'].get(key,{}).get('percent_val',0))
                    nation_yes_val.append(response[val]['national'].get(key,{}).get('value',0))

            for key in s_keys:
                if key=='1':
                    
                    # state_no.append(response[val]['state'].get(key,{}).get('percent_val',0))
                # elif key!=None and key!='0':
                    #logic here is the response has only three keys for all columns so if its not these two then it should be the column name
                    #saves time to avoid writing down all column yes names and then verifying
                    state_yes.append(response[val]['state'].get(key,{}).get('percent_val',0))
                    state_yes_val.append(response[val]['state'].get(key,{}).get('value',0))

    else:
        for val in column_names:
            n_keys=response[val]['national'].keys()
            s_keys=response[val]['state'].keys()
            # print("n keys", n_keys, "s keys", s_keys)
            for key in n_keys:
                if key=='1':
                    # nation_no.append(response[val]['national'].get(key,{}).get('percent_val',0))
                # elif key!=None and key!='0': 
                    nation_yes.append(response[val]['national'].get(key,{}).get('percent_val',0))

            for key in s_keys:
                if key=='1':
                    # state_no.append(sum(item.get('percentage', 0) for item in response[val]['state'].get(key, [])))
                # elif key!=None and key!='0':
                    state_yes.append([{'column': val, 'percentage': item.get('percentage', 0)} for item in response[val]['state'].get(key, [])])
                    #logic here is the response has only three keys for all columns so if its not these two then it should be the column name
                    #saves time to avoid writing down all column yes names and then verifying
                    # state_yes.append(response[val]['state'].get(key,{}).get('percent_val',0))
    new_response = {'state_yes':state_yes,'nation_yes':nation_yes, 'state_yes_val': state_yes_val, 'nation_yes_val': nation_yes_val}
    print("SONA RESPONSE", new_response)
    y_axis=['Elementary School Playbook: A Guide for Grades K-5','Middle Level Playbook: A Guide for Grades 5-8','High School Playbook','Special Olympics State Playbook','Special Olympics Fitness Guide for Schools','Unified Physical Education Resource',
            'Special Olympics Young Athletes Activity Guide','Inclusive Youth Leadership Training: Faciliatator Guide','Planning and Hosting a Youth Leadership Experience','Unified Classoom lessons and activities','Generation Unified Youtube channel or videos',
            'Inclusion Tiles game or facilitator guide']
    
    title='Percentage of liaisons who found SONA resources useful in State Program {0} vs. National data'.format(dashboard_filters['state_abv'])
    state=dashboard_filters['state_abv']
    # return horizontal_bar_graph(response,y_axis,title,state, compare_type=type)
    print(new_response)
    if new_response["state_yes_val"] or new_response["nation_yes_val"]:
        return horizontal_stacked_bar(new_response,y_axis,title,state, compare_type=type, getImage = getImage)
    else:
        return None


'''   
CHARTS
'''
def horizontal_bar_graph(response,y_axis,heading,state,compare_type="default", getImage = False):
    # print("horizontal_bar_graph", response, compare_type)

    fig = go.Figure()
    colors = ['rgba(200, 200, 220, 0.8)', 'rgba(168, 184, 134, 0.8)', 'rgba(170, 180, 200, 0.8)', 'rgba(109, 154, 168, 0.8)', 'rgba(120, 130, 160, 0.8)', 'rgba(140, 138, 173, 0.8)']     # Define your colors here with opacity
    # Get the list of dictionaries for key '1'
    # Create a bar for each dictionary in state_data
    if compare_type == "default":
        fig.add_trace(go.Bar(
        y=y_axis,
        x=[round(response[val]['national'].get('1',{}).get('percent_val',0)) for val in response if response],
        name='National',
        customdata=[response[val]['national'].get('1',{}).get('value',0) for val in response if response],
        orientation='h',
        hovertemplate='%{x}%, %{customdata} schools, %{y}',

        visible = "legendonly",
        marker=dict(
            color='rgba(246, 78, 139, 0.6)',
            line=dict(color='rgba(246, 78, 139, 1.0)', width=0)
            
                  )
            ))
        # print("fig 1")

        # print("PRINT DEFAULT")
        fig.add_trace(go.Bar(
        y=y_axis,
        x=[round(response[val]['state'].get('1',{}).get('percent_val',0)) for val in response if response ],
        customdata=[response[val]['state'].get('1',{}).get('value',0) for val in response if response],

        name=state,
        orientation='h',
        hovertemplate='%{x}%, %{customdata} schools, %{y}',

        marker=dict(
            color='rgba(58, 71, 80, 0.6)',
            line=dict(color='rgba(58, 71, 80, 1.0)', width=0)
        )
      ))
    else:
        for i, val in enumerate(response):
            # print("horizontal_graph_state_data1", val)
            state_data = response[val]['state']
            # Create a bar for each key in state_data
            # print("horizontal_graph_state_data", state_data)
            for key in state_data:
                if key is '1':  # Exclude None key
                    state_data[key] = sorted(state_data[key], key=lambda x: x.get('percentage', 0), reverse=True)
                    for j, level_data in enumerate(state_data[key]):
                        # print("horizontal_graph_level_data", level_data, y_axis[i], i)
                        fig.add_trace(go.Bar(
                            y=[y_axis[i]],
                            x=[round(level_data.get('percentage', 0))],
                            name=f"{state} {y_axis[i]} Level {get_horizontal_bar_legend_name(level_data, compare_type)} ",
                            orientation='h',
                            offsetgroup=1,
                            hovertemplate=f"{round(level_data.get('percentage', 0))}%, {level_data.get('total', 0)} schools, Level {get_horizontal_bar_legend_name(level_data, compare_type)}",
                            width=0.5,
                            # base=j*1.1,  # Shift each bar slightly
                            # Add this line to increase the width of the bars
                            marker=dict(
                                color=colors[j % len(colors)],  # Use the index to select a color
                                line=dict(color=colors[j % len(colors)], width=0)
                        )))
                        # print(f"fig {val} Level {level_data.get('implementation_level')}")


    # fig.update_traces(visible=False, showLegend=True selector=dict(name="National"))


    fig.update_layout( 
        title={
            'text': heading,
            'x': 0.5,  # Center the title
            # 'xanchor': 'center',  # Ensure the title doesn't move
        },
        barmode='group',
       
        height=500,  # Adjust the height of the graph
        # margin=dict(l=100, r=50, b=100, t=100, pad=4),
        xaxis=dict(title="Percentage value (%)"),  # This line is added to reverse the order of categories on y-axis
         legend=dict(
             traceorder='reversed'
              )
        
    )
    print("GETIMAGE:", getImage)
    if getImage:
        img_bytes = io.BytesIO()
        py.write_image(fig, img_bytes, format='png')
        img_bytes.seek(0)
        print(img_bytes)
        return img_bytes
    else:
        plot_div = plot(fig, output_type='div', include_plotlyjs=False)
        return plot_div
    
def get_horizontal_bar_legend_name(data, type="default"):
    match type:
        case 'imp_level':
            match data['implementation_level']:
                case '1':
                     return 'Emerging'
                case '2':
                     return 'Developing'
                case '3':
                     return 'Full Implementation'
        case 'locale':
            return data['grouped_locale']
        case 'school_level':
            match data['gradeLevel_WithPreschool']:
                case '1.00':
                    return 'Elementary'
                case '2.00':
                    return 'High'
                case '3.00':
                    return 'Middle'
                case '4.00':
                    return 'Preschool'
        case 'survey_taken_year':
            match data['survey_taken_year']:
                case 2018:
                    return '2018'
                case 2019:
                    return '2019'
                case 2020:
                    return '2020'
                case 2021:
                    return '2021'
                case 2022:
                    return '2022'
                case 2023:
                    return '2023'

                
    return 'none'            





def horizontal_stacked_bar(response,y_axis,heading,state, compare_type="default", getImage = False):
    # print("SONA RESULT", response)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=y_axis,
        x=[round(val) for val in response['nation_yes']],
        customdata=response['nation_yes_val'],
        name='National',
        visible = "legendonly",
        hovertemplate='%{x}%, %{customdata} schools, %{y}',
        orientation='h',
        marker=dict(
            color='rgba(99, 110, 250, 0.8)',
            line=dict(color='rgba(99, 110, 250, 1.0)', width=0)
        )
    ))
    if compare_type == "default":
        fig.add_trace(go.Bar(
            y=y_axis,
            x=[round(val) for val in response['state_yes']],
            customdata=response['state_yes_val'],
            name=state,
            hovertemplate='%{x}%, %{customdata} schools, %{y}',
            orientation='h',
            marker=dict(
                color='rgba(139, 144, 209, 0.8)',
                line=dict(color='rgba(139, 144, 209, 1)', width=0)
            )
        ))
    else:
        for i, val in enumerate(response['state_yes']):
            # print("horizontal_stacked_bar", val)
            # state_data = response[val]['state']
            # # Create a bar for each key in state_data
            # print("horizontal_graph_state_data", state_data)
            # for key in state_data:
            #     if key is '1':  # Exclude None key
            val = sorted(val, key=lambda x: x.get('percentage', 0), reverse=True)
            # print("horizontal_stacked_bar val", val)
                    # for j, level_data in enumerate(state_data[key]):
                    #     print("horizontal_graph_level_data", level_data, y_axis[i], i)
                    #     fig.add_trace(go.Bar(
                    #         y=[y_axis[i]],
                    #         x=[level_data.get('percentage', 0)],
                    #         name=f"{state} {y_axis[i]} Level {get_horizontal_bar_legend_name(level_data, compare_type)} ",
                    #         orientation='h',
                    #         offsetgroup=1,
                    #         hovertemplate=f"{level_data.get('percentage', 0)} Level {get_horizontal_bar_legend_name(level_data, compare_type)}",
                    #         width=0.5,  # Add this line to increase the width of the bars
                    #         marker=dict(
                    #             color=colors[j % len(colors)],  # Use the index to select a color
                    #             line=dict(color=colors[j % len(colors)], width=0)
                    #     )))
                    #     print(f"fig {val} Level {level_data.get('implementation_level')}")

    fig.update_layout(title=heading,barmode='group',xaxis_range=[0,100], xaxis_title="Percentage value (%)", width=1400, height=500)
    if getImage:
        img_bytes = io.BytesIO()
        py.write_image(fig, img_bytes, format='png')
        img_bytes.seek(0)
        return img_bytes   
    else:    
        plot_div = plot(fig, output_type='div', include_plotlyjs=False)
        return plot_div

