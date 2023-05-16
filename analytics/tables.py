from django.shortcuts import render
from plotly.offline import plot
import plotly.graph_objects as go
from django.http import HttpResponseRedirect
from django.db.models import Count
from .forms import Filters
from analytics.models import SchoolDetails
from authenticate.models import CustomUser
from django.contrib.auth.decorators import login_required
from analytics.views import state_choices

'''gives filters for queries after removing values which will not be there in table'''
def filter_set(dashboard_filters):
    filters = []
    for key,val in dashboard_filters.items():
        if val != 'all': #avoiding all beacuse all is not a value in table 
            filters.append((key,val))
    filters = dict(filters)
    return filters
        
def school_locale_data(dashboard_filters):
    #headline__startswith="Rural"
    filters = filter_set(dashboard_filters)
    print('Filters:',filters)
    return SchoolDetails.objects.filter(**filters).values_list('locale')

def school_level_data(dashboard_filters,state_abv_=None):
    keys = ['Elementary','Middle','High','Other','Preschool']
    filters = filter_set(dashboard_filters)
    data = dict(SchoolDetails.objects.values_list('gradeLevel_WithPreschool').filter(**filters).annotate(total = Count('implementation_level')))
    for val in keys:
        if val not in data.keys():
            data[val]=0
    print("LOGGER:",data)
    return data #{str(key):val for key,val in data}

def school_enrollment_data(dashboard_filters,state_abv_=None):
    filters = filter_set(dashboard_filters)
    data = SchoolDetails.objects.values_list('student_enrollment_range').filter(**filters).annotate(total = Count('student_enrollment_range'))
    return {str(key):val for key,val in data}

def school_lunch_data(dashboard_filters,state_abv_=None):
    filters = filter_set(dashboard_filters)
    data = SchoolDetails.objects.values_list('student_free_reduced_lunch').filter(**filters).annotate(total = Count('student_free_reduced_lunch'))
    return {str(key):val for key,val in data}

def school_minority_data(dashboard_filters,state_abv_=None):
    filters = filter_set(dashboard_filters)
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

def school_locale_graph(dashboard_filters):
    locale_data = school_locale_data(dashboard_filters)
    locale_statecount={'Rural':0,'Town':0,'Suburb':0,'City':0}
    for val in locale_data:
        key  = val[0].split(':')[0]
        if key in locale_statecount.keys(): 
            locale_statecount[key] +=1


    locale_state = percentage_values(locale_statecount)
    
    total_locale_data=school_locale_data(dashboard_filters)
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

def school_level_graph(dashboard_filters):
    school_level = school_level_data(dashboard_filters,state_abv_=dashboard_filters['state_abv'])
    national_level = school_level_data(dashboard_filters)
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

def school_student_enrollment(dashboard_filters):
    student_enroll_state = school_enrollment_data(dashboard_filters,dashboard_filters['state_abv'])
    student_enroll_nation = school_enrollment_data(dashboard_filters)
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

def school_free_reduce_lunch(dashboard_filters):
    student_lunch_state = school_lunch_data(dashboard_filters,dashboard_filters['state_abv'])
    student_lunch_nation = school_lunch_data(dashboard_filters)
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

def school_minority(dashboard_filters):
    minority_state = school_minority_data(dashboard_filters,dashboard_filters['state_abv'])
    minority_nation = school_minority_data(dashboard_filters)
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


def frequency_of_leadership(dashboard_filters):
    response = {'special_education_teachers':{},'general_education_teachers':{},'physical_education_teachers':{},'adapted_pe_teachers':{},'athletic_director':{},'students_with_idd':{},
                'students_without_idd':{},'school_administrators':{},'parents_of_students_with_idd':{},'parents_of_students_without_idd':{},'school_psychologist':{},'special_olympics_state_program_staff':{}}
    filters=filter_set(dashboard_filters)
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

def load_dashboard(dashboard_filters,dropdown):
    context ={
        'table_plot_1':school_locale_graph(dashboard_filters),
        'table_plot_2':school_level_graph(dashboard_filters),
        'table_plot_3':school_student_enrollment(dashboard_filters),
        'table_plot_4':school_free_reduce_lunch(dashboard_filters),
        'table_plot_5':school_minority(dashboard_filters),
        'table_plot_6':frequency_of_leadership(dashboard_filters),
        'form':dropdown,
    }
    return context

@login_required(login_url='../auth/login')
def tables(request):
    state = CustomUser.objects.values('state').filter(username=request.user)[0]
    state=state.get('state','None')
    if request.method=='GET':
        filter_state = state
        if state=='all':
            filter_state = 'ma'# on inital load some data has to be displayed so defaulting to ma
        context = load_dashboard(dashboard_filters={'state_abv':filter_state,'survey_taken_year':2022},dropdown=Filters(state=state_choices(state)))
      
    if request.method=='POST':
        state = state_choices(state)
        dropdown = Filters(state,request.POST)
        print(dropdown)
        if dropdown.is_valid():
            dashboard_filters = dropdown.cleaned_data
            context = load_dashboard(dashboard_filters,dropdown)
            
    return render(request, 'analytics/tables.html', context)          
