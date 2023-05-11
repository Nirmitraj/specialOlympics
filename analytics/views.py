from django.shortcuts import render
from plotly.offline import plot
import plotly.graph_objects as go
import plotly.express as px
from django.http import HttpResponseRedirect
from django.db.models import Sum,Count,Max
from .forms import Filters
from analytics.models import SchoolDetails
import pandas as pd



state_abv_ ='ma'
dashboard_filters={'state_abv':'sca','survey_taken_year':2022}
test_f=Filters()
def dropdown(request):
    global state_abv_
    global dashboard_filters
    global test_f
    if request.method=='POST':
        f = Filters(request.POST)

        if f.is_valid():
            test_f=f
            if request.path=='/filter_welcome/':
                page='/welcome.html'
            elif request.path=='/filter_tables/':
                page='/tables.html'
            print("CLEANED DATA:",f.cleaned_data)
            state_abv_ = f.cleaned_data['state_abv']
            dashboard_filters = f.cleaned_data
            print('htmlsample_1:',f)
            render(request, 'analytics'+page, {'form':f})
            return HttpResponseRedirect(page)
    
    if request.method=='GET':
        f=Filters()
    print('htmlsample_2:',f)
    return render(request, 'analytics'+page, {'form':f})


def index(request):
    def filter_set():
        filters = []
        for key,val in dashboard_filters.items():
            if val != 'all':
                filters.append((key,val))
        filters = dict(filters)
        return filters
    
    def core_experience_data(key,range,survey_year=None):
        select_names = {'sports':'unified_sports_component',
                        'leadership':'youth_leadership_component',
                        'whole_school':'whole_school_component'}
        
        filters = filter_set()
        filters_national=filter_set()
        if range == 'national':
            filters_national.pop('state_abv')
            filters = filters_national

        if survey_year:
            filters["survey_taken_year"] = survey_year
        if key:
            data = dict(SchoolDetails.objects.values_list(select_names[key]).filter(**filters).annotate(total = Count(select_names[key])))
            data = data.get(True,0) #considering only partipated people
            return data
        else:
            return 0
    
    def survey_years():
        survey_years = SchoolDetails.objects.values_list('survey_taken_year',flat=True).distinct().order_by('survey_taken_year')
        return list(survey_years)
    
    def core_experience_year_data():
        survey_year= survey_years()
        response = {'sports':[],'leadership':[],'whole_school':[],'survey_year':survey_year,'state_sports':[],'state_leadership':[],'state_whole_school':[]}
        for year in survey_year:
            response['sports'].append(core_experience_data('sports',survey_year=year,range='national'))
            response['leadership'].append(core_experience_data('leadership',survey_year=year,range='national'))
            response['whole_school'].append(core_experience_data('whole_school',survey_year=year,range='national'))
            response['state_sports'].append(core_experience_data('sports',survey_year=year,range='state'))
            response['state_leadership'].append(core_experience_data('leadership',survey_year=year,range='state'))
            response['state_whole_school'].append(core_experience_data('whole_school',survey_year=year,range='state'))            
        return response
    
    def implementation_level_data():
        filters = filter_set()
        survey_year = survey_years()

        response = {"emerging":[0]*len(survey_year),"developing":[0]*len(survey_year),"full_implement":[0]*len(survey_year),"survey_year":[0]*len(survey_year),
                    "state_emerging":[0]*len(survey_year),"state_developing":[0]*len(survey_year),"state_full_implement":[0]*len(survey_year)}
        index = 0
        filters = filter_set()
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
        filters_state = filter_set()
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


    def school_suvery_data():
        filters= filter_set()
        filters.pop('state_abv') # as this graph is for all states we remove state filter for this
        return SchoolDetails.objects.values('school_state','survey_taken').filter(**filters).annotate(total = Count('survey_taken')).order_by('school_state')

    def school_survey():
        school_surveys = school_suvery_data()
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

        layout = dict(
            title='School survey ratio',
            yaxis = dict(range=[min(survey_true), max(survey_true)]),
            barmode='group',
        )

        fig = go.Figure(data=trace, layout=layout)
        fig.update_layout(width=1400, height=500)
        plot_div = plot(fig, output_type='div', include_plotlyjs=False)
        return plot_div
    
    def core_experience():
        # survey_year=SchoolDetails.objects.aggregate(Max('survey_taken_year'))
        # survey_year = survey_year['survey_taken_year__max']
        filters = filter_set()
        sports=core_experience_data('sports',range='state')
        leadership = core_experience_data('leadership',range='state')
        wholeschool = core_experience_data('whole_school',range='state')

        print(sports,leadership,wholeschool)
        core_exp_df = pd.DataFrame(dict(
            lables = ['sports','leadership','wholeschool'],
            values = [sports,leadership,wholeschool]
        ))

        fig = px.pie(core_exp_df, values='values', names='lables',title='Core experience implementation in {year} {state_abv}'.format(state_abv=filters['state_abv'],year=filters['survey_taken_year']))
        plot_div = plot(fig, output_type='div', include_plotlyjs=False)
        return plot_div
    
    def implementation_level():
        data=implementation_level_data()
        
        print("IMPLEVEL:",data)
        df = pd.DataFrame(data)
        fig = px.line(df, x=df['survey_year'], y=df['emerging'], labels={"survey_year":"year","emerging":"implementation"})#color???
        fig.add_scatter(x=df['survey_year'],y=df['emerging'], name="emerging")
        fig.add_scatter(x=df['survey_year'],y=df['developing'], name="developing")#color="developing")
        fig.add_scatter(x=df['survey_year'],y=df['full_implement'], name="full_implement")#,color="full_implemention")
        fig.add_scatter(x=df['survey_year'],y=df['state_emerging'], name="state_emerging")
        fig.add_scatter(x=df['survey_year'],y=df['state_developing'], name="state_developing")
        fig.add_scatter(x=df['survey_year'],y=df['state_full_implement'], name="state_full_implement")

        fig.update_layout( 
        legend=dict(
            title="implementation level", orientation="h", y=1, yanchor="bottom", x=0.5, xanchor="center"
        ),
        xaxis = dict (
            tickmode='linear',
            tick0 = min(df['survey_year']),
            dtick=1
        )
    )
        plot_div = plot(fig, output_type='div', include_plotlyjs=False)

        return plot_div
    
    def core_experience_yearly():
        filters = filter_set()
        data = core_experience_year_data()

        print("CORE_EXP_YEAR:",data)
        df = pd.DataFrame(data)
        fig = px.line(df, x=df['survey_year'], y=df['state_sports'], labels={"survey_year":"year","sports":"core experience"})
        fig.add_scatter(x=df['survey_year'],y=df['sports'], name="Unified sports")
        fig.add_scatter(x=df['survey_year'],y=df['leadership'], name="Inclusive youth leadership")
        fig.add_scatter(x=df['survey_year'],y=df['whole_school'], name="Whole school engagement")
        fig.add_scatter(x=df['survey_year'],y=df['state_sports'], name="{state} Unified sports".format(state=filters['state_abv']))
        fig.add_scatter(x=df['survey_year'],y=df['state_leadership'], name="{state} Inclusive youth leadership".format(state=filters['state_abv']))
        fig.add_scatter(x=df['survey_year'],y=df['state_whole_school'], name="{state} school engagement".format(state=filters['state_abv']))
        title_name = "Core experience implementation over time in {0}".format(filters['state_abv'])

        fig.update_layout( 
        legend=dict(
            title=title_name, orientation="h", y=1, yanchor="bottom", x=0.5, xanchor="center"
        ),
        xaxis = dict (
            tickmode='linear',
            tick0 = min(df['survey_year']),
            dtick=1
        ) )
        plot_div = plot(fig, output_type='div', include_plotlyjs=False)

        return plot_div
    
    context ={
        'plot1': school_survey(),
        'plot2': core_experience(),
        'plot3':implementation_level(),
        'plot4':core_experience_yearly(),
        'plot5':implement_unified_sport_activity(),
        'plot6':implement_youth_leadership_activity(),
        'plot7':implement_school_engagement_activity(),
        'plot8':sona_resources_useful(),
        'form':test_f,#Filters(request.POST)
    }

    return render(request, 'analytics/welcome.html', context)
    
        
def tables(request):
    '''gives filters for queries after removing values which will not be there in table'''
    def filter_set():
        filters = []
        for key,val in dashboard_filters.items():
            if val != 'all': #avoiding all beacuse all is not a value in table 
                filters.append((key,val))
        filters = dict(filters)
        return filters
            
    def school_locale_data():
        #headline__startswith="Rural"
        filters = filter_set()
        print('Filters:',filters)
        return SchoolDetails.objects.filter(**filters).values_list('locale')

    def school_level_data(state_abv_=None):
        keys = ['Elementary','Middle','High','Other','Preschool']
        filters = filter_set()
        data = dict(SchoolDetails.objects.values_list('gradeLevel_WithPreschool').filter(**filters).annotate(total = Count('implementation_level')))
        for val in keys:
            if val not in data.keys():
                data[val]=0
        print("LOGGER:",data)
        return data #{str(key):val for key,val in data}
    
    def school_enrollment_data(state_abv_=None):
        filters = filter_set()
        data = SchoolDetails.objects.values_list('student_enrollment_range').filter(**filters).annotate(total = Count('student_enrollment_range'))
        return {str(key):val for key,val in data}
    
    def school_lunch_data(state_abv_=None):
        filters = filter_set()
        data = SchoolDetails.objects.values_list('student_free_reduced_lunch').filter(**filters).annotate(total = Count('student_free_reduced_lunch'))
        return {str(key):val for key,val in data}
    
    def school_minority_data(state_abv_=None):
        filters = filter_set()
        data = SchoolDetails.objects.values_list('student_nonwhite_population').filter(**filters).annotate(total = Count('student_nonwhite_population'))
        return {str(key):val for key,val in data} 
    
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

    def school_locale_graph():
        locale_data = school_locale_data()
        locale_statecount={'Rural':0,'Town':0,'Suburb':0,'City':0}
        for val in locale_data:
            key  = val[0].split(':')[0]
            if key in locale_statecount.keys(): 
                locale_statecount[key] +=1


        locale_state = percentage_values(locale_statecount)
        
        total_locale_data=school_locale_data()
        locale_nationcount={'Rural':0,'Town':0,'Suburb':0,'City':0}
        for val in total_locale_data:
            key = val[0].split(':')[0]
            if key in locale_statecount.keys():
                locale_nationcount[key] +=1

        locale_nation = percentage_values(locale_nationcount)


        fig1 = go.Figure(data=[go.Table(
            header=dict(values=['School locale', 'State 2022 year %','National 2022 year %'],
                        line_color='darkslategray',
                        fill_color='lightskyblue',
                        align='left'),
            cells=dict(values=[['Rural', 'Town','Suburban','Urban'],
                            [locale_state['Rural']['percent_val'], locale_state['Town']['percent_val'], locale_state['Suburb']['percent_val'], locale_state['City']['percent_val']],
                            [locale_nation['Rural']['percent_val'], locale_nation['Town']['percent_val'], locale_nation['Suburb']['percent_val'], locale_nation['City']['percent_val']]], 
                        line_color='darkslategray',
                        fill_color='lightcyan',
                        align='left'))
        ])

        fig1.update_layout(width=700, height=300,title='Characteristics of schoolslocale in {year}, for the state {state_abv}'.format(year=dashboard_filters['survey_taken_year'],state_abv=dashboard_filters['state_abv']))
        plot_div = plot(fig1, output_type='div', include_plotlyjs=False)
        return plot_div
    
    def school_level_graph():
        school_level = school_level_data(state_abv_=dashboard_filters['state_abv'])
        national_level = school_level_data()
        school_level=percentage_values(school_level)
        national_level=percentage_values(national_level)
        print('School level',school_level,national_level)
        fig2 = go.Figure(data=[go.Table(header=dict(values=['School level', 'State 2022 year %','National 2022 year %']),
                        cells=dict(values=[['Elementary','Middle','High','Other','Preschool'], 
                                            [school_level['Elementary']['percent_val'], school_level['Middle']['percent_val'], school_level['High']['percent_val'], school_level['Other']['percent_val'],school_level['Preschool']['percent_val']],
                                            [national_level['Elementary']['percent_val'],national_level['Middle']['percent_val'],national_level['High']['percent_val'],national_level['Other']['percent_val'],national_level['Preschool']['percent_val']]]))
                            ])

        fig2.update_layout(width=700, height=350,title='Characteristics of schools level in {year}, for the state {state_abv}'.format(state_abv=dashboard_filters['state_abv'],year=dashboard_filters['survey_taken_year']))
        plot_div = plot(fig2, output_type='div', include_plotlyjs=False)
        return plot_div
    
    def school_student_enrollment(state_abv_):
        student_enroll_state = school_enrollment_data(dashboard_filters['state_abv'])
        student_enroll_nation = school_enrollment_data()
        student_enroll_state = percentage_values(student_enroll_state)
        student_enroll_nation = percentage_values(student_enroll_nation)
        print(student_enroll_state,student_enroll_nation)
        fig3 = go.Figure(data=[go.Table(header=dict(values=['Student enrollment', 'State 2022 year %','National 2022 year %']),
                        cells=dict(values=[['< 500','501-1000','1001-1500','More than 1500'], 
                                           [student_enroll_state.get('<500',{}).get('percent_val',0), student_enroll_state.get('501-1000',{}).get('percent_val',0), student_enroll_state.get('1001-1500',{}).get('percent_val',0), student_enroll_state.get('>1500',{}).get('percent_val',0)],
                                           [student_enroll_nation.get('<500',{}).get('percent_val',0), student_enroll_nation.get('501-1000',{}).get('percent_val',0), student_enroll_nation.get('1001-1500',{}).get('percent_val',0), student_enroll_nation.get('>1500',{}).get('percent_val',0)],]))])

        fig3.update_layout(width=700, height=350,title='Characteristics of school_student_enrollment in {year}, for the state {state_abv}'.format(state_abv=dashboard_filters['state_abv'],year=dashboard_filters['survey_taken_year']))
        plot_div = plot(fig3, output_type='div', include_plotlyjs=False)
        return plot_div

    def school_free_reduce_lunch():
        student_lunch_state = school_lunch_data(dashboard_filters['state_abv'])
        student_lunch_nation = school_lunch_data()
        student_lunch_state=percentage_values(student_lunch_state)
        student_lunch_nation=percentage_values(student_lunch_nation)
        print('school_free_reduce_lunch:',student_lunch_state,student_lunch_nation)
        fig4 = go.Figure(data=[go.Table(header=dict(values=['Student Receiving free or reduced lunch%', 'State 2022 year %','National 2022 year %']),
                        cells=dict(values=[['0-25','26-50','51-75','76-100'], 
                                           [student_lunch_state.get("0%-25%",{}).get('percent_val','Nill'),student_lunch_state.get("26%-50%",{}).get('percent_val','Nill'), student_lunch_state.get("51%-75%",{}).get('percent_val','Nill'), student_lunch_state.get("76%-100%",{}).get('percent_val','Nill')],
                                           [student_lunch_nation.get("0%-25%",{}).get('percent_val','Nill'),student_lunch_nation.get("26%-50%",{}).get('percent_val','Nill'), student_lunch_nation.get("51%-75%",{}).get('percent_val','Nill'), student_lunch_nation.get("76%-100%",{}).get('percent_val','Nill')]]))
                            ])
        fig4.update_layout(width=700, height=350,title='Characteristics of school free reduced lunch in {year}, for the state {state_abv}'.format(state_abv=dashboard_filters['state_abv'],year=dashboard_filters['survey_taken_year']))
        plot_div = plot(fig4, output_type='div', include_plotlyjs=False)
        return plot_div
    
    def school_minority():
        minority_state = school_minority_data(dashboard_filters['state_abv'])
        minority_nation = school_minority_data()
        minority_state=percentage_values(minority_state)
        minority_nation=percentage_values(minority_nation)
        print('student_minority:',minority_state,minority_nation)
        fig5 = go.Figure(data=[go.Table(header=dict(values=['Students of racial/ethnic minority %', 'State 2022 year %','National 2022 year %']),
                 cells=dict(values=[['< 10','11-25','26-50','51-75','76-90','> 90'], 
                                    [minority_state.get('10% or less',{}).get('percent_val','Nill'), minority_state.get('11%-25%',{}).get('percent_val','Nill'), minority_state.get('26%-50%',{}).get('percent_val','Nill'), minority_state.get('51%-75%',{}).get('percent_val','Nill'), minority_state.get('76%-90%',{}).get('percent_val','Nill'),minority_state.get('More than 90%',{}).get('percent_val','Nill')],
                                    [minority_nation.get('10% or less',{}).get('percent_val','Nill'), minority_state.get('11%-25%',{}).get('percent_val','Nill'),minority_nation.get('26%-50%',{}).get('percent_val','Nill'),minority_nation.get('51%-75%',{}).get('percent_val','Nill'),minority_nation.get('76%-90%',{}).get('percent_val','Nill'),minority_nation.get('More than 90%',{}).get('percent_val','Nill')]]))
                     ])
        fig5.update_layout(width=800, height=370,title='Characteristics of Students of racial/ethnic minority in {year}, for the state {state_abv}'.format(state_abv=dashboard_filters['state_abv'],year=dashboard_filters['survey_taken_year']))
        plot_div = plot(fig5, output_type='div', include_plotlyjs=False)
        return plot_div
    

    context ={
        'table_plot_1':school_locale_graph(),
        'table_plot_2':school_level_graph(),
        'table_plot_3':school_student_enrollment(state_abv_),
        'table_plot_4':school_free_reduce_lunch(),
        'table_plot_5':school_minority(),
        'table_plot_6':frequency_of_leadership(),
        'form':test_f,
    }
    return render(request,'analytics/tables.html',context)


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

def filter_set():
    filters = []
    for key,val in dashboard_filters.items():
        if val != 'all':
            filters.append((key,val))
    filters = dict(filters)
    return filters
    
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
def implement_unified_sport_activity():
    response={'sports_sports_teams':{}, 'sports_unified_PE':{},'sports_unified_fitness':{},
             'sports_unified_esports':{},'sports_young_athletes':{},'sports_unified_developmental_sports':{}}
    filters=filter_set()
    for column_name in response.keys():
        response[column_name]['national']=percentage_values(main_query(column_name,filters,key='all')) 
        response[column_name]['state']=percentage_values(main_query(column_name,filters,key='state'))
    y_axis = ['Unified Sports Teams', 'Unified PE', 'Unified fitness','unified esports', 'young athletes(participants)', 'Unified Developmental Sports']
    title='Percentage of schools implementing each Unified Sports activity'
    return horizontal_bar_graph(response,y_axis,title)

def implement_youth_leadership_activity():
    response = {'leadership_unified_inclusive_club':{},'leadership_youth_training':{},'leadership_athletes_volunteer':{},
               'leadership_youth_summit':{},'leadership_activation_committe':{}}
    filters=filter_set()
    for column_name in response.keys():
        response[column_name]['national']=percentage_values(main_query(column_name,filters,key='all')) 
        response[column_name]['state']=percentage_values(main_query(column_name,filters,key='state'))
    y_axis=['unifed/Inclusive Club','Inclusive Youth leadership Training/Class','Young Athletes Volunteers','Youth summit','Youth Activation Committee']
    title='Percentage of schools implementing each Inclusive Youth Leadership activity'
    return horizontal_bar_graph(response,y_axis,title)

def implement_school_engagement_activity():
    response = {'engagement_spread_word_campaign':{},'engagement_fansinstands':{},'engagement_sports_day':{},
                'engagement_fundraisingevent':{},'engagement_SO_play':{},'engagement_fitness_challenge':{}}
    
    filters=filter_set()
    for column_name in response.keys():
        response[column_name]['national']=percentage_values(main_query(column_name,filters,key='all')) 
        response[column_name]['state']=percentage_values(main_query(column_name,filters,key='state'))
    y_axis=['Spread the word'+'<br>'+'Inclusion/Respect/Disabilityy' +'<br>'+'Awareness Campaign','Unified Sports pep Rally','Unified Sports Day/Festival','Fundraising events /activities','Special Olympics play/performance','Unified Fitness Challenge']
    title='Percentage of schools implementing each Inclusive Whole School Engagement activity'
    return horizontal_bar_graph(response,y_axis,title)

def frequency_of_leadership():
    response = {'special_education_teachers':{},'general_education_teachers':{},'physical_education_teachers':{},'adapted_pe_teachers':{},'athletic_director':{},'students_with_idd':{},
                'students_without_idd':{},'school_administrators':{},'parents_of_students_with_idd':{},'parents_of_students_without_idd':{},'school_psychologist':{},'special_olympics_state_program_staff':{}}
    filters=filter_set()
    for column_name in response.keys():
        response[column_name]['national']=percentage_values(main_query(column_name,filters,key='all')) 
        response[column_name]['state']=percentage_values(main_query(column_name,filters,key='state'))

    #finding what is considering as yes in the tables the below dict is a what varible in column is equal to yes
    yes_response = {'special_education_teachers':'Special Education teachers','general_education_teachers':'General Education teachers','physical_education_teachers':'Physical Education teachers',
                           'adapted_pe_teachers':'Adapted PE teachers','athletic_director':'Athletic director','students_with_idd':'Students with IDD',
                'students_without_idd':'Students without IDD','school_administrators':'School Administrators','parents_of_students_with_idd':'Parents of students with IDD',
                'parents_of_students_without_idd':'Parents of students without IDD','school_psychologist':'School Psychologist/Counselor/Social Worker','special_olympics_state_program_staff':'SO state staff'}
    state_values= [] 
    national_values=[]
    y_axis=['Special Education Teachers','Students without IDD','Student with IDD','School Administrators','General Education Teachers','Physical Education (PE) Teachers ',
            'Athletic Director','Adapted PE teachers','Parents of Students with IDD','Parents of Students without IDD','School Psychologist/Counselor/Social Worker','Special Olympics State Program Staff']
    for key,yes_val in yes_response.items():
        state_values.append(response[key]['state'].get(yes_val,{}).get('percent_val',0))
        national_values.append(response[key]['national'].get(yes_val,{}).get('percent_val',0))
    new_response = {'state_values':state_values,'national_values':national_values,'lables':y_axis} #Main response to go out of this functions
    title='Frequency of Leadership Team membership among common types of participants'
    headers=['Participant','state_name','National'] 

    return table_graph(new_response,title,headers,y_axis)

def sona_resources_useful():
    response={'elementary_school_playbook':{},'middle_level_playbook':{},'high_school_playbook':{},'special_olympics_state_playbook':{},'special_olympics_fitness_guide_for_schools':{},'unified_physical_education_resource':{},
              'special_olympics_young_athletes_activity_guide':{},'inclusive_youth_leadership_training_faciliatator_guide':{},'planning_and_hosting_a_youth_leadership_experience':{},'unified_classoom_lessons_and_activities':{},'generation_unified_youtube_channel_or_videos':{},'inclusion_tiles_game_or_facilitator_guide':{}}
    column_names=response.keys()
    filters=filter_set()
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
    
    title='Percentage of liaisons who found SONA resources useful'
    return horizontal_stacked_bar(new_response,y_axis,title)


'''   
CHARTS
'''
def horizontal_bar_graph(response,y_axis,heading):
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
        x=[response[val]['state'].get('Yes',{}).get('percent_val',0) for val in response if response],
        name='state',
        orientation='h',
        marker=dict(
            color='rgba(58, 71, 80, 0.6)',
            line=dict(color='rgba(58, 71, 80, 1.0)', width=0)
        )
    ))

    fig.update_layout(title=heading,barmode='group',xaxis_range=[0,100])
    plot_div = plot(fig, output_type='div', include_plotlyjs=False)
    return plot_div
    
def table_graph(new_response,heading,headers,y_column):
    headerColor = 'grey'
    rowEvenColor = 'lightgrey'
    rowOddColor = 'white'

    fig = go.Figure(data=[go.Table(
    header=dict(
        values=headers,
        line_color='darkslategray',
        fill_color=headerColor,
        align=['left','center'],
        font=dict(color='white', size=12)
    ),
    cells=dict(
        values=[
        y_column,
        new_response['state_values'],
        new_response['national_values']],
        line_color='darkslategray',
        # 2-D list of colors for alternating rows
        fill_color = [[rowOddColor,rowEvenColor,rowOddColor, rowEvenColor,rowOddColor]*5],
        align = ['left', 'center'],
        font = dict(color = 'darkslategray', size = 11)
        ))
    ])

    fig.update_layout(title=heading, width=700, height=600)
    plot_div = plot(fig, output_type='div', include_plotlyjs=False)
    return plot_div

def horizontal_stacked_bar(response,y_axis,heading):
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
        name='state',
        orientation='h',
        marker=dict(
            color='rgba(139, 144, 209, 0.8)',
            line=dict(color='rgba(139, 144, 209, 1)', width=0)
        )
    ))

    fig.update_layout(title=heading,barmode='group',xaxis_range=[0,100], width=1400, height=500)

    plot_div = plot(fig, output_type='div', include_plotlyjs=False)
    return plot_div




# {'elementary_school_playbook': {'national': {None: {'value': 0, 'percent_val': 0.0}, '0': {'value': 905, 'percent_val': 66.7}, 'Elementary School Playbook: A Guide for Grades K-5': {'value': 452, 'percent_val': 33.3}}, 'state': {None: {'value': 0, 'percent_val': 0.0}, '0': {'value': 21, 'percent_val': 75.0}, 'Elementary School Playbook: A Guide for Grades K-5': {'value': 7, 'percent_val': 25.0}}}, 'middle_level_playbook': {'national': {None: {'value': 0, 'percent_val': 0.0}, '0': {'value': 874, 'percent_val': 74.6}, 'Middle Level Playbook: A Guide for Grades 5-8': {'value': 298, 'percent_val': 25.4}}, 'state': {None: {'value': 0, 'percent_val': 0.0}, '0': {'value': 17, 'percent_val': 81.0}, 'Middle Level Playbook: A Guide for Grades 5-8': {'value': 4, 'percent_val': 19.0}}}, 'high_school_playbook': {'national': {None: {'value': 0, 'percent_val': 0.0}, 'High School Playbook': {'value': 504, 'percent_val': 37.8}, '0': {'value': 829, 'percent_val': 62.2}}, 'state': {None: {'value': 0, 'percent_val': 0.0}, 'High School Playbook': {'value': 17, 'percent_val': 58.6}, '0': {'value': 12, 'percent_val': 41.4}}}, 'special_olympics_state_playbook': {'national': {None: {'value': 0, 'percent_val': 0.0}, 'Special Olympics ${e://Field/State} Playbook': {'value': 390, 'percent_val': 29.3}, '0': {'value': 941, 'percent_val': 70.7}}, 'state': {None: {'value': 0, 'percent_val': 0.0}, '0': {'value': 19, 'percent_val': 86.4}, 'Special Olympics ${e://Field/State} Playbook': {'value': 3, 'percent_val': 13.6}}}, 'special_olympics_fitness_guide_for_schools': {'national': {None: {'value': 0, 'percent_val': 0.0}, 'Special Olympics Fitness Guide for Schools': {'value': 269, 'percent_val': 21.6}, '0': {'value': 976, 'percent_val': 78.4}}, 'state': {None: {'value': 0, 'percent_val': 0.0}, '0': {'value': 19, 'percent_val': 76.0}, 'Special Olympics Fitness Guide for Schools': {'value': 6, 'percent_val': 24.0}}}, 'unified_physical_education_resource': {'national': {None: {'value': 0, 'percent_val': 0.0}, '0': {'value': 828, 'percent_val': 65.8}, 'Unified Physical Education Resource': {'value': 431, 'percent_val': 34.2}}, 'state': {None: {'value': 0, 'percent_val': 0.0}, '0': {'value': 19, 'percent_val': 70.4}, 'Unified Physical Education Resource': {'value': 8, 'percent_val': 29.6}}}, 'special_olympics_young_athletes_activity_guide': {'national': {None: {'value': 0, 'percent_val': 0.0}, 'Special Olympics Young Athletes Activity Guide': {'value': 411, 'percent_val': 34.2}, '0': {'value': 791, 'percent_val': 65.8}}, 'state': {None: {'value': 0, 'percent_val': 0.0}, '0': {'value': 19, 'percent_val': 86.4}, 'Special Olympics Young Athletes Activity Guide': {'value': 3, 'percent_val': 13.6}}}, 'inclusive_youth_leadership_training_faciliatator_guide': {'national': {None: {'value': 0, 'percent_val': 0.0}, '0': {'value': 873, 'percent_val': 85.3}, 'Inclusive Youth Leadership Training: Facilitator Guide': {'value': 150, 'percent_val': 14.7}}, 'state': {None: {'value': 0, 'percent_val': 0.0}, '0': {'value': 24, 'percent_val': 82.8}, 'Inclusive Youth Leadership Training: Facilitator Guide': {'value': 5, 'percent_val': 17.2}}}, 'planning_and_hosting_a_youth_leadership_experience': {'national': {None: {'value': 0, 'percent_val': 0.0}, '0': {'value': 722, 'percent_val': 94.1}, 'Planning and Hosting a Youth Leadership Experience: A Group Youth Engagement Activity Resource': {'value': 45, 'percent_val': 5.9}}, 'state': {None: {'value': 0, 'percent_val': 0.0}, '0': {'value': 16, 'percent_val': 94.1}, 'Planning and Hosting a Youth Leadership Experience: A Group Youth Engagement Activity Resource': {'value': 1, 'percent_val': 5.9}}}, 'unified_classoom_lessons_and_activities': {'national': {'Unified Classroom lessons and activities': {'value': 524, 'percent_val': 39.7}, None: {'value': 0, 'percent_val': 0.0}, '0': {'value': 796, 'percent_val': 60.3}}, 'state': {None: {'value': 0, 'percent_val': 0.0}, 'Unified Classroom lessons and activities': {'value': 11, 'percent_val': 45.8}, '0': {'value': 13, 'percent_val': 54.2}}}, 'generation_unified_youtube_channel_or_videos': {'national': {'Generation Unified YouTube channel or Generation Unified videos': {'value': 360, 'percent_val': 37.5}, None: {'value': 0, 'percent_val': 0.0}, '0': {'value': 601, 'percent_val': 62.5}}, 'state': {None: {'value': 0, 'percent_val': 0.0}, '0': {'value': 7, 'percent_val': 41.2}, 'Generation Unified YouTube channel or Generation Unified videos': {'value': 10, 'percent_val': 58.8}}}, 'inclusion_tiles_game_or_facilitator_guide': {'national': {'0': {'value': 637, 'percent_val': 72.2}, None: {'value': 0, 'percent_val': 0.0}, 'Inclusion Tiles game/activity or Inclusion Tiles Facilitator Guide': {'value': 245, 'percent_val': 27.8}}, 'state': {None: {'value': 0, 'percent_val': 0.0}, '0': {'value': 13, 'percent_val': 68.4}, 'Inclusion Tiles game/activity or Inclusion Tiles Facilitator Guide': {'value': 6, 'percent_val': 31.6}}}}