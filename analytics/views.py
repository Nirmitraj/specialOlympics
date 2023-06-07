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


state_abv_ = 'sc'
    
''' This sends filters in to django querys 
    if all is present in input we remove
    that as it is eqvivalent of all in query'''

def filter_set(dashboard_filters):
    filters = []
    for key,val in dashboard_filters.items():
        if val != 'all':
            filters.append((key,val))
    filters = dict(filters)
    return filters

def core_exp_percentage(state,year):
    print(state,year)
    national_sum_1 = SchoolDetails.objects.values_list('unified_sports_component').filter(unified_sports_component=1,survey_taken_year=year).annotate(total = Count('unified_sports_component'))[0][1]
    print(national_sum_1)
    national_sum_2 = SchoolDetails.objects.values_list('youth_leadership_component').filter(youth_leadership_component=1,survey_taken_year=year).annotate(total = Count('youth_leadership_component'))[0][1]
    national_sum_3 = SchoolDetails.objects.values_list('whole_school_component').filter(whole_school_component=1,survey_taken_year=year).annotate(total = Count('whole_school_component'))[0][1]
    state_sum_1=SchoolDetails.objects.values_list('unified_sports_component').filter(state_abv=state,unified_sports_component=1,survey_taken_year=year).annotate(total = Count('unified_sports_component'))[0][1]
    state_sum_2=SchoolDetails.objects.values_list('youth_leadership_component').filter(state_abv=state,youth_leadership_component=1,survey_taken_year=year).annotate(total = Count('youth_leadership_component'))[0][1]
    state_sum_3=SchoolDetails.objects.values_list('whole_school_component').filter(state_abv=state,whole_school_component=1,survey_taken_year=year).annotate(total = Count('whole_school_component'))[0][1]
    national_sum = national_sum_1 + national_sum_2 + national_sum_3
    state_sum = state_sum_1+state_sum_2 +state_sum_3
    return national_sum,state_sum

def core_experience_data(dashboard_filters,key,range,survey_year=None):
    select_names = {'sports':'unified_sports_component',
                    'leadership':'youth_leadership_component',
                    'whole_school':'whole_school_component'}
    
    filters = filter_set(dashboard_filters)
    filters_national=filter_set(dashboard_filters)
    if survey_year:
        filters["survey_taken_year"] = survey_year
        national_sum,state_sum = core_exp_percentage(state=filters['state_abv'],year=survey_year)
    if range == 'national':
        filters_national.pop('state_abv')
        filters = filters_national

    if key:#key value for selectnames dictionary
        data = dict(SchoolDetails.objects.values_list(select_names[key]).filter(**filters).annotate(total = Count(select_names[key])))
        data = data.get(True,0) #considering only partipated people
        if survey_year:
            if filters.get('state_abv',False):
                data=round(((data/state_sum)*100),2)
            else:
                data=round(((data/national_sum)*100),2)
            return data
        return data
    else:
        return 0

def survey_years():
    survey_years = SchoolDetails.objects.values_list('survey_taken_year',flat=True).distinct().order_by('survey_taken_year')
    return list(survey_years)


def core_experience_year_data(dashboard_filters):
    survey_year= survey_years()
    response = {'sports':[],'leadership':[],'whole_school':[],'survey_year':survey_year,'state_sports':[],'state_leadership':[],'state_whole_school':[]}
    for year in survey_year:
        response['sports'].append(core_experience_data(dashboard_filters,'sports',survey_year=year,range='national'))
        response['leadership'].append(core_experience_data(dashboard_filters,'leadership',survey_year=year,range='national'))
        response['whole_school'].append(core_experience_data(dashboard_filters,'whole_school',survey_year=year,range='national'))
        response['state_sports'].append(core_experience_data(dashboard_filters,'sports',survey_year=year,range='state'))
        response['state_leadership'].append(core_experience_data(dashboard_filters,'leadership',survey_year=year,range='state'))
        response['state_whole_school'].append(core_experience_data(dashboard_filters,'whole_school',survey_year=year,range='state'))            
    return response

def implementation_level_data(dashboard_filters):
    filters = filter_set(dashboard_filters)
    survey_year = survey_years()

    response = {"emerging":[0]*len(survey_year),"developing":[0]*len(survey_year),"full_implement":[0]*len(survey_year),"survey_year":[0]*len(survey_year),
                "state_emerging":[0]*len(survey_year),"state_developing":[0]*len(survey_year),"state_full_implement":[0]*len(survey_year)}
    index = 0
    filters = filter_set(dashboard_filters)
    filters.pop('state_abv')

    for year in survey_year:
        filters['survey_taken_year'] = year
        national_data = SchoolDetails.objects.values('implementation_level','survey_taken_year').filter(**filters).annotate(total = Count('implementation_level')).order_by('implementation_level')
        print(national_data,filters)
        for val in national_data:
            if val['implementation_level'] == 'Emerging':
                response["emerging"][index] = val.get('total',0)
            elif val['implementation_level'] == 'Developing':
                response["developing"][index] = val.get('total',0)
            elif val['implementation_level'] == 'Full-implementation':
                response["full_implement"][index] = val.get('total',0)
                response["survey_year"][index] = val.get('survey_taken_year',0)
        index+=1

    index = 0
    filters_state = filter_set(dashboard_filters)
    for year in survey_year:
        filters_state['survey_taken_year'] = year
        state_data = SchoolDetails.objects.values('implementation_level','survey_taken_year').filter(**filters_state).annotate(total = Count('implementation_level')).order_by('implementation_level')

        for val in state_data:
            if val['implementation_level'] == 'Emerging':
                response["state_emerging"][index] = val.get('total',0)
            elif val['implementation_level'] == 'Developing':
                response["state_developing"][index] = val.get('total',0)
            elif val['implementation_level'] == 'Full-implementation':
                response["state_full_implement"][index] = val.get('total',0)
        index+=1

    print('implementation_level_data',response)
    return response


def implementation_level(dashboard_filters):
    data=implementation_level_data(dashboard_filters)
    #data = implementation_level_percent(dashboard_filters)

    print("IMPLEVEL:",data)
    df = pd.DataFrame(data)

    fig = px.line(df, x=df['survey_year'], y=df['emerging'], labels={"survey_year":"year","emerging":"Implementation level"})#color???
    fig.add_scatter(x=df['survey_year'],y=df['emerging'], name="Emerging")
    fig.add_scatter(x=df['survey_year'],y=df['state_emerging'], name="{0} Emerging".format(dashboard_filters['state_abv']))   
    fig.add_scatter(x=df['survey_year'],y=df['developing'], name="Developing")#color="developing")
    fig.add_scatter(x=df['survey_year'],y=df['state_developing'], name="{0} Developing".format((dashboard_filters['state_abv'])))   
    fig.add_scatter(x=df['survey_year'],y=df['full_implement'], name="Full implementation".format(dashboard_filters['state_abv']))#,color="full_implemention")
    fig.add_scatter(x=df['survey_year'],y=df['state_full_implement'], name="{0} Full implementation".format(dashboard_filters['state_abv']))
    title_name = 'Implementation level over time,<br> National vs. State Program in state {0}'.format(dashboard_filters['state_abv'])
    fig.update_layout( 
    title={
        'text': title_name,
        'y': 0.95,  # Adjust the y position of the title (0 - bottom, 1 - top)
        'x': 0.5  # Adjust the x position of the title (0 - left, 0.5 - center, 1 - right)
    },
    legend=dict(
        orientation="h",
    ),
    xaxis = dict (
        tickmode='linear',
        tick0 = min(df['survey_year']),
        dtick=1
    ))
    plot_div = plot(fig, output_type='div', include_plotlyjs=False)
    return plot_div


def school_suvery_data(dashboard_filters):
    filters= filter_set(dashboard_filters)
    filters.pop('state_abv') # as this graph is for all states we remove state filter for this
    print('Filterssssss',filters)
    return SchoolDetails.objects.values('school_state','survey_taken').filter(**filters).exclude(school_state='-99').annotate(total = Count('survey_taken')).order_by('school_state')

def school_survey(dashboard_filters):
    school_surveys = school_suvery_data(dashboard_filters)
    data_json={}
    for val in school_surveys:
        if val['school_state'] not in data_json.keys():
            data_json[val['school_state']] = {}
            #data_json[val['school_state']][val['survey_taken']] = 0
        data_json[val['school_state']][str(val['survey_taken'])]=val['total']

    school_state = list(data_json.keys())
    survey_true = [data_json[i].get('True',0) for i in school_state]
    survey_false =[data_json[i].get('False',0) for i in school_state]

    trace = [go.Bar(x= school_state,y = survey_true,name='Yes'),
            go.Bar(x= school_state,y = survey_false,name='No')]
    year = dashboard_filters['survey_taken_year']
    print('YEAR',year)
    layout = dict(
        title='Year {0} ({1}) State Program response rate'.format(int(year)-2008,year),
        yaxis = dict(range=[min(survey_true), max(survey_true)]),
        barmode='group',
    )

    fig = go.Figure(data=trace, layout=layout)
    fig.update_layout(width=1400, height=500)
    plot_div = plot(fig, output_type='div', include_plotlyjs=False)
    return plot_div

def core_experience(dashboard_filters):
    # survey_year=SchoolDetails.objects.aggregate(Max('survey_taken_year'))
    # survey_year = survey_year['survey_taken_year__max']
    filters = filter_set(dashboard_filters)
    sports=core_experience_data(dashboard_filters,'sports',range='state')
    leadership = core_experience_data(dashboard_filters,'leadership',range='state')
    wholeschool = core_experience_data(dashboard_filters,'whole_school',range='state')

    print(sports,leadership,wholeschool)
    core_exp_df = pd.DataFrame(dict(
        lables = ['sports','leadership','wholeschool'],
        values = [sports,leadership,wholeschool]
    ))

    fig = px.pie(core_exp_df, values='values', names='lables',title='Core experience implementation in {year} {state_abv}'.format(state_abv=filters['state_abv'],year=filters['survey_taken_year']))
    plot_div = plot(fig, output_type='div', include_plotlyjs=False)
    return plot_div

def core_experience_yearly(dashboard_filters):
    filters = filter_set(dashboard_filters)
    data = core_experience_year_data(dashboard_filters)

    print("CORE_EXP_YEAR:",data)
    #{'sports': [6370, 3461], 'leadership': [3914, 2560], 'whole_school': [5132, 3361], 'survey_year': [2021, 2022], 'state_sports': [47, 21], 'state_leadership': [18, 12], 'state_whole_school': [26, 18]}
            
    df = pd.DataFrame(data)
    fig = px.line(df, x=df['survey_year'], y=df['state_sports'], labels={"survey_year":"year","state_sports":"core experience"})
    fig.add_scatter(x=df['survey_year'],y=df['sports'], name="Unified sports")
    fig.add_scatter(x=df['survey_year'],y=df['state_leadership'], name="{state} Inclusive youth leadership".format(state=filters['state_abv']))
    fig.add_scatter(x=df['survey_year'],y=df['whole_school'], name="Whole school engagement")
    fig.add_scatter(x=df['survey_year'],y=df['state_sports'], name="{state} Unified sports".format(state=filters['state_abv']))
    fig.add_scatter(x=df['survey_year'],y=df['leadership'], name="Inclusive youth leadership")
    fig.add_scatter(x=df['survey_year'],y=df['state_whole_school'], name="{state} school engagement".format(state=filters['state_abv']))
    title_name = "Percentage of Core experience implementation over time,<br> National vs State program in state {0}".format(filters['state_abv'])

    fig.update_layout( 
    title={
        'text': title_name,
        'y': 0.95,  # Adjust the y position of the title (0 - bottom, 1 - top)
        'x': 0.5  # Adjust the x position of the title (0 - left, 0.5 - center, 1 - right)
    },
    legend=dict(
        orientation="h",
    ),
    xaxis = dict (
        tickmode='linear',
        tick0 = min(df['survey_year']),
        dtick=1
    ) )
    plot_div = plot(fig, output_type='div', include_plotlyjs=False)
    return plot_div


def load_dashboard(dashboard_filters,dropdown):
        context={
            'plot1':school_survey(dashboard_filters),
            'plot2':core_experience(dashboard_filters),
            'plot3':implementation_level(dashboard_filters),
            'plot4':core_experience_yearly(dashboard_filters),
            'plot5':implement_unified_sport_activity(dashboard_filters),
            'plot6':implement_youth_leadership_activity(dashboard_filters),
            'plot7':implement_school_engagement_activity(dashboard_filters),
            'plot8':sona_resources_useful(dashboard_filters),
            'form':dropdown
        }
        return context



@login_required(login_url='../auth/login/')
def index(request):
    state = CustomUser.objects.values('state').filter(username=request.user)[0]
    state=state.get('state','None')
    if request.method=='GET':
        filter_state = state
        if state=='all':
            filter_state = 'ak'# on inital load some data has to be displayed so defaulting to ma
        context = load_dashboard(dashboard_filters={'state_abv':filter_state,'survey_taken_year':2022},dropdown=Filters(state=state_choices(state)))
    
    if request.method=='POST':
        state = state_choices(state)
        dropdown = Filters(state,request.POST)
        print(dropdown)
        if dropdown.is_valid():
            #print('heloooooo')
            dashboard_filters = dropdown.cleaned_data
            context = load_dashboard(dashboard_filters,dropdown)
            
            #return HttpResponseRedirect('/')
    return render(request, 'analytics/welcome.html', context)          
  
     


'''
Utility functions
'''

'''
input list or single dict 
return list of percent values or returns nested dict with value and percent
op sample :'state': {None: {'value': 0, 'percent_val': 0.0}, 'Yes': {'value': 4, 'percent_val': 7.0}, 'No': {'value': 53, 'percent_val': 93.0}}}
'''
def percentage_values(total_values):
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
def main_query(column_name,filters,key): 
    if key=='state':
        filters=filters
    if key=='all':
        filters=filters.copy()
        filters.pop('state_abv')
        print(filters)
    data = dict(SchoolDetails.objects.values_list(column_name).filter(**filters).annotate(total = Count(column_name)))
    print(data)
    #test query to run in terminal: dict(SchoolDetails.objects.values_list('sports_sports_teams').filter(state_abv='sca',survey_taken_year=2022).annotate(total = Count('sports_sports_teams')))
    return data



'''
LOGIC
'''
def implement_unified_sport_activity(dashboard_filters):
    response={'sports_sports_teams':{}, 'sports_unified_PE':{},'sports_unified_fitness':{},
             'sports_unified_esports':{},'sports_young_athletes':{},'sports_unified_developmental_sports':{}}
    filters=filter_set(dashboard_filters)
    for column_name in response.keys():
        response[column_name]['national']=percentage_values(main_query(column_name,filters,key='all')) 
        response[column_name]['state']=percentage_values(main_query(column_name,filters,key='state'))
    y_axis = ['Unified Sports Teams', 'Unified PE', 'Unified fitness','Unified esports', 'Young athletes(participants)', 'Unified Developmental Sports']
    title='Percentage of schools implementing each <br> Unified Sports activity in {0} compared to national data'.format(dashboard_filters['state_abv'])
    state=dashboard_filters['state_abv']#adding state to the response for graph lables
    return horizontal_bar_graph(response,y_axis,title,state)

def implement_youth_leadership_activity(dashboard_filters):
    response = {'leadership_unified_inclusive_club':{},'leadership_youth_training':{},'leadership_athletes_volunteer':{},
               'leadership_youth_summit':{},'leadership_activation_committe':{}}
    filters=filter_set(dashboard_filters)
    for column_name in response.keys():
        response[column_name]['national']=percentage_values(main_query(column_name,filters,key='all')) 
        response[column_name]['state']=percentage_values(main_query(column_name,filters,key='state'))
    y_axis=['Unifed/Inclusive Club','Inclusive Youth leadership Training/Class','Young Athletes Volunteers','Youth summit','Youth Activation Committee']
    title='Percentage of schools implementing each <br>  Youth Leadership activity in {0} compared to national data'.format(dashboard_filters['state_abv'])
    state=dashboard_filters['state_abv']#adding state to the response for graph lables
    return horizontal_bar_graph(response,y_axis,title,state)

def implement_school_engagement_activity(dashboard_filters):
    response = {'engagement_spread_word_campaign':{},'engagement_fansinstands':{},'engagement_sports_day':{},
                'engagement_fundraisingevent':{},'engagement_SO_play':{},'engagement_fitness_challenge':{}}
    
    filters=filter_set(dashboard_filters)
    for column_name in response.keys():
        response[column_name]['national']=percentage_values(main_query(column_name,filters,key='all')) 
        response[column_name]['state']=percentage_values(main_query(column_name,filters,key='state'))
    y_axis=['Spread the word'+'<br>'+'Inclusion/Respect/Disability' +'<br>'+'Awareness Campaign','Unified Sports pep Rally','Unified Sports Day/Festival','Fundraising events /activities','Special Olympics play/performance','Unified Fitness Challenge']
    title='Percentage of schools implementing each <br> Inclusive Whole School Engagement activity {0} compared to national data'.format(dashboard_filters['state_abv'])
    state=dashboard_filters['state_abv']#adding state to the response for graph lables
    return horizontal_bar_graph(response,y_axis,title,state)


def sona_resources_useful(dashboard_filters):
    response={'elementary_school_playbook':{},'middle_level_playbook':{},'high_school_playbook':{},'special_olympics_state_playbook':{},'special_olympics_fitness_guide_for_schools':{},'unified_physical_education_resource':{},
              'special_olympics_young_athletes_activity_guide':{},'inclusive_youth_leadership_training_faciliatator_guide':{},'planning_and_hosting_a_youth_leadership_experience':{},'unified_classoom_lessons_and_activities':{},'generation_unified_youtube_channel_or_videos':{},'inclusion_tiles_game_or_facilitator_guide':{}}
    column_names=response.keys()
    filters=filter_set(dashboard_filters)
    for column_name in response.keys():
        response[column_name]['national']=percentage_values(main_query(column_name,filters,key='all')) 
        response[column_name]['state']=percentage_values(main_query(column_name,filters,key='state'))

    ##seperating yes and no keys from each parent key
    state_no=[]
    nation_no=[]
    state_yes=[]
    nation_yes=[]
    for val in column_names:
        n_keys=response[val]['national'].keys()
        s_keys=response[val]['state'].keys()
        for key in n_keys:
            if key=='0':
                nation_no.append(response[val]['national'].get(key,{}).get('percent_val',0))
            elif key!=None and key!='0': 
                #logic here is the response has only three keys for all columns so if its not these two then it should be the column name
                #saves time to avoid writing down all column yes names and then verifying
                nation_yes.append(response[val]['national'].get(key,{}).get('percent_val',0))

        for key in s_keys:
            if key=='0':
                state_no.append(response[val]['state'].get(key,{}).get('percent_val',0))
            elif key!=None and key!='0':
                #logic here is the response has only three keys for all columns so if its not these two then it should be the column name
                #saves time to avoid writing down all column yes names and then verifying
                state_yes.append(response[val]['state'].get(key,{}).get('percent_val',0))
    
    new_response = {'state_yes':state_yes,'state_no':state_no,'nation_yes':nation_yes,'nation_no':nation_no}
    
    y_axis=['Elementary School Playbook: A Guide for Grades K-5','Middle Level Playbook: A Guide for Grades 5-8','High School Playbook','Special Olympics State Playbook','Special Olympics Fitness Guide for Schools','Unified Physical Education Resource',
            'Special Olympics Young Athletes Activity Guide','Inclusive Youth Leadership Training: Faciliatator Guide','Planning and Hosting a Youth Leadership Experience','Unified Classoom lessons and activities','Generation Unified Youtube channel or videos',
            'Inclusion Tiles game or facilitator guide']
    
    title='Percentage of liaisons who found SONA resources useful in State {0} compared to national data'.format(dashboard_filters['state_abv'])
    state=dashboard_filters['state_abv']
    return horizontal_stacked_bar(new_response,y_axis,title,state)


'''   
CHARTS
'''
def horizontal_bar_graph(response,y_axis,heading,state):
    print(response)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=y_axis,
        x=[response[val]['national'].get('Yes',{}).get('percent_val',0) for val in response if response],
        name='National',
        orientation='h',
        marker=dict(
            color='rgba(246, 78, 139, 0.6)',
            line=dict(color='rgba(246, 78, 139, 1.0)', width=0)
        )
    ))
    fig.add_trace(go.Bar(
        y=y_axis,
        x=[response[val]['state'].get('Yes',{}).get('percent_val',0) for val in response if response ],
        name=state,
        orientation='h',
        marker=dict(
            color='rgba(58, 71, 80, 0.6)',
            line=dict(color='rgba(58, 71, 80, 1.0)', width=0)
        )
    ))

    fig.update_layout( 
    title={
        'text': heading,
        # 'y': 0.95,  # Adjust the y position of the title (0 - bottom, 1 - top)
        'x': 0.5  # Adjust the x position of the title (0 - left, 0.5 - center, 1 - right)
    },barmode='group',xaxis_range=[0,100])

    plot_div = plot(fig, output_type='div', include_plotlyjs=False)
    return plot_div
    

def horizontal_stacked_bar(response,y_axis,heading,state):
    print(response)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=y_axis,
        x=response['nation_yes'],
        name='National',
        orientation='h',
        marker=dict(
            color='rgba(99, 110, 250, 0.8)',
            line=dict(color='rgba(99, 110, 250, 1.0)', width=0)
        )
    ))
    fig.add_trace(go.Bar(
        y=y_axis,
        x=response['state_yes'],
        name=state,
        orientation='h',
        marker=dict(
            color='rgba(139, 144, 209, 0.8)',
            line=dict(color='rgba(139, 144, 209, 1)', width=0)
        )
    ))

    fig.update_layout(title=heading,barmode='group',xaxis_range=[0,100], width=1400, height=500)

    plot_div = plot(fig, output_type='div', include_plotlyjs=False)
    return plot_div
