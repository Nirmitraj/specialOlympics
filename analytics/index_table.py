import copy
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
    # print('Filters:',filters)
    return SchoolDetails.objects.filter(**filters).values_list('locale')

def school_level_data(dashboard_filters,state_abv_=None):
    keys = ['Elementary','Middle','High','Other','Preschool']
    filters = filter_set(dashboard_filters)

    data = dict(SchoolDetails.objects.values_list('gradeLevel_WithPreschool').filter(**filters).annotate(total = Count('implementation_level')))
    for val in keys:
        if val not in data.keys():
            data[val]=0
    # print("Grade Level in Preschool:",data)
    return data #{str(key):val for key,val in data}

def categorize_enrollment(enrollment):
    if enrollment is None:
        return 'NULL'
    elif enrollment < 500:
        return '< 500'
    elif 500 <= enrollment <= 1000:
        return '500-1000'
    elif 1001 <= enrollment <= 1500:
        return '1001-1500'
    elif 1501 <= enrollment <= 2000:
        return '1501-2000'
    else:
        return '> 2000'


from django.db.models import Count, Case, When, IntegerField

def school_enrollment_data(dashboard_filters, state_abv_=None):
    filters = filter_set(dashboard_filters)
    data = SchoolDetails.objects.values_list('student_enrollment_range').filter(**filters).annotate(total = Count('student_enrollment_range'))
    print("SCHOOL ENROLLMENT", data)
    return {str(key):val for key,val in data}

def school_lunch_data(dashboard_filters,state_abv_=None):
    filters = filter_set(dashboard_filters)
    data = SchoolDetails.objects.values_list('student_free_reduced_lunch').filter(**filters).annotate(total = Count('student_free_reduced_lunch'))
    print("School lunch", data)
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
    state_name=dashboard_filters['state_abv']
    locale_data = school_locale_data(dashboard_filters)
    # print("locale graph", locale_data)
    locale_statecount={'Rural':0,'Town':0,'Suburb':0,'City':0}
    for val in locale_data:
        if isinstance(val[0], str):

            key  = val[0].split(':')[0]
            if key in locale_statecount.keys():
                locale_statecount[key] +=1

    # print("locale graph 1", locale_statecount)

    
    locale_state = percentage_values(locale_statecount)
    # print("locale graph 2", locale_state)

    
    # filters=dashboard_filters
    # filters.pop('state_abv')
    filters =copy.copy(dashboard_filters)
    filters.pop('state_abv')
    if "county" in filters:
        filters.pop("county")
    total_locale_data=school_locale_data(filters)
    # print(total_locale_data)

    locale_nationcount={'Rural':0,'Town':0,'Suburb':0,'City':0}
    for val in total_locale_data:
        if isinstance(val[0], str):

            key = val[0].split(':')[0]
            if key in locale_statecount.keys():#same keys both national and state
                locale_nationcount[key] +=1

    locale_nation = percentage_values(locale_nationcount)


    fig1 = go.Figure(data=[go.Table(
        header=dict(values=['Locale',  state_name+' '+str(dashboard_filters['survey_taken_year']) + " %",'National '+ str(dashboard_filters['survey_taken_year']) + " %"],
                    line_color='white',
                    align='left'),
        cells=dict(values=[['Rural', 'Town','Suburban','Urban'],
                        [locale_state['Rural']['percent_val'], locale_state['Town']['percent_val'], locale_state['Suburb']['percent_val'], locale_state['City']['percent_val']],
                        [locale_nation['Rural']['percent_val'], locale_nation['Town']['percent_val'], locale_nation['Suburb']['percent_val'], locale_nation['City']['percent_val']]], 
                    line_color='white',
                    align='left'))
    ])

    fig1.update_layout(width=900, height=390,font_size=15,title='Characteristics of schools locale in {year}, for the State Program {state_abv}'.format(state_abv=state_name,year=dashboard_filters['survey_taken_year']))
    plot_div = plot(fig1, output_type='div', include_plotlyjs=False)
    return plot_div

def school_level_graph(dashboard_filters):
    school_level = school_level_data(dashboard_filters,state_abv_=dashboard_filters['state_abv'])
    filters =copy.copy(dashboard_filters)
    filters.pop('state_abv')
    if "county" in filters:
        filters.pop("county")
    national_level=school_level_data(filters)#sending no state filters gives national data
    school_level=percentage_values(school_level)
    national_level=percentage_values(national_level)
    # print('School level',school_level,national_level)
    state_name=dashboard_filters['state_abv']
    '''
    1.00==Elementary
    2.00==Middle
    3.00==High
    4.00==Preschool
    9.00==Other
    '''
    fig2 = go.Figure(data=[go.Table(header=dict(values=['School level', state_name +' '+str(dashboard_filters['survey_taken_year']) + " %",'National '+ str(dashboard_filters['survey_taken_year']) + " %"]),
                    cells=dict(values=[['Elementary','Middle','High','Other','Preschool'], 
                                        [school_level.get('1.00',{}).get('percent_val',0), school_level.get('2.00',{}).get('percent_val',0), school_level.get('3.00',{}).get('percent_val',0), school_level.get('9.00',{}).get('percent_val',0),school_level.get('4.00',{}).get('percent_val',0)],
                                        [national_level.get('1.00',{}).get('percent_val',0),national_level.get('2.00',{}).get('percent_val',0),national_level.get('3.00',{}).get('percent_val',0),national_level.get('9.00',{}).get('percent_val',0),national_level.get('4.00',{}).get('percent_val',0)]
                                        ]))])

    fig2.update_layout(width=900, height=350,font_size=15,title='Characteristics of schools level in {year}, for the State Program {state_abv}'.format(state_abv=state_name,year=dashboard_filters['survey_taken_year']))
    plot_div = plot(fig2, output_type='div', include_plotlyjs=False)
    return plot_div

def school_student_enrollment(dashboard_filters):
    print("DASHBOARD FILTERS", dashboard_filters)
    
    # Get state-specific enrollment data
    student_enroll_state = school_enrollment_data(dashboard_filters, dashboard_filters.get('state_abv'))
    print("STUDENT ENROLL STATE", student_enroll_state)
    if student_enroll_state is None:
        print("DEBUG: student_enroll_state is None")
        student_enroll_state = {}  # Ensure it's an empty dictionary if None
    else:
        print("DEBUG: student_enroll_state", student_enroll_state)
    
    # Remove 'state_abv' and 'county' from filters for national data
    filters = copy.copy(dashboard_filters)
    filters.pop('state_abv', None)
    filters.pop('county', None)
    
    # Get national enrollment data
    student_enroll_nation = school_enrollment_data(filters)
    if student_enroll_nation is None:
        print("DEBUG: student_enroll_nation is None")
        student_enroll_nation = {}  # Ensure it's an empty dictionary if None
    else:
        print("DEBUG: student_enroll_nation", student_enroll_nation)
    
    # Calculate percentage values
    student_enroll_state = percentage_values(student_enroll_state)
    student_enroll_nation = percentage_values(student_enroll_nation)
    print("student_enroll_state", student_enroll_state)
    print("student_enroll_nation", student_enroll_nation)

    state_name = dashboard_filters.get('state_abv', 'State')
    categories = ['< 500', '500-1000', '1001-1500', '1501-2000', '> 2000']
    category_keys = ['1.00', '2.00', '3.00', '4.00', '5.00']  # Use integers, matching the earlier annotation

    # Create the table with Plotly
    fig3 = go.Figure(data=[go.Table(
        header=dict(values=['Student enrollment', f'{state_name} {dashboard_filters.get("survey_taken_year", "Year")} %', f'National {dashboard_filters.get("survey_taken_year", "Year")} %']),
        cells=dict(values=[
            categories,
            [student_enroll_state.get(key, {}).get('percent_val', 0) for key in category_keys],
            [student_enroll_nation.get(key, {}).get('percent_val', 0) for key in category_keys]
        ])
    )])

    # Update layout
    fig3.update_layout(width=900, height=350, font_size=15, title=f'Percentage of schools at each student enrollment level <br> in {dashboard_filters.get("survey_taken_year", "Year")}, for the State Program {state_name}')
    
    # Generate the plot as a div
    plot_div = plot(fig3, output_type='div', include_plotlyjs=False)
    return plot_div


def school_free_reduce_lunch(dashboard_filters):
    student_lunch_state = school_lunch_data(dashboard_filters,dashboard_filters['state_abv'])
    filters =copy.copy(dashboard_filters)
    filters.pop('state_abv')
    if "county" in filters:
        filters.pop("county")
    student_lunch_nation = school_lunch_data(filters)
    student_lunch_state=percentage_values(student_lunch_state)
    student_lunch_nation=percentage_values(student_lunch_nation)
    # print('school_free_reduce_lunch:',student_lunch_state,student_lunch_nation)
    state_name=dashboard_filters['state_abv']
    '''
    1.00==0-25
    2.00==26-50
    3.00==26-50
    4.00==26-50
    '''
    fig4 = go.Figure(data=[go.Table(header=dict(values=[' % of Student receiving free or reduced lunch', state_name+' '+str(dashboard_filters['survey_taken_year']) + " %",'National '+ str(dashboard_filters['survey_taken_year']) + " %"]),
                    cells=dict(values=[['0-25','26-50','26-50','26-50'], 
                                        [student_lunch_state.get("1.00",{}).get('percent_val','0'),student_lunch_state.get("2.00",{}).get('percent_val','0'), student_lunch_state.get("3.00",{}).get('percent_val','0'), student_lunch_state.get("4.00",{}).get('percent_val','0')],
                                        [student_lunch_nation.get("1.00",{}).get('percent_val','0'),student_lunch_nation.get("2.00",{}).get('percent_val','0'), student_lunch_nation.get("3.00",{}).get('percent_val','0'), student_lunch_nation.get("4.00",{}).get('percent_val','0')]]))
                        ])
    fig4.update_layout(  title={
        'text':'Percentage of schools with students receiving <br>free or reduced-price lunch in {year}, for the State Program {state_abv}'.format(state_abv=dashboard_filters['state_abv'],year=dashboard_filters['survey_taken_year']),
        'x': 0.5  # Adjust the x position of the title (0 - left, 0.5 - center, 1 - right)
    },
        width=900, height=350,font_size=15)
    plot_div = plot(fig4, output_type='div', include_plotlyjs=False)
    return plot_div

def school_minority(dashboard_filters):
    minority_state = school_minority_data(dashboard_filters,dashboard_filters['state_abv'])
    filters =copy.copy(dashboard_filters)
    filters.pop('state_abv')
    if "county" in filters:
        filters.pop("county")
    minority_nation = school_minority_data(filters)
    minority_state=percentage_values(minority_state)
    minority_nation=percentage_values(minority_nation)
    # print('student_minority:',minority_state,minority_nation)
    state_name=dashboard_filters['state_abv']
    '''
    1.00==< 10
    2.00==11-25
    3.00==26-50
    4.00==51-75
    5.00==76-90
    6.00==> 90
    '''
    fig5 = go.Figure(data=[go.Table(header=dict(values=['% of racial/ethnic minority students', state_name+' '+str(dashboard_filters['survey_taken_year'])+ " %",'National '+ str(dashboard_filters['survey_taken_year'])+ " %"]),
                cells=dict(values=[['< 10','11-25','26-50','51-75','76-90','> 90'], 
                                [minority_state.get('1.00',{}).get('percent_val','0'), minority_state.get('2.00',{}).get('percent_val','0'), minority_state.get('3.00',{}).get('percent_val','0'), minority_state.get('4.00',{}).get('percent_val','0'), minority_state.get('5.00',{}).get('percent_val','0'),minority_state.get('6.00',{}).get('percent_val','0')],
                                [minority_nation.get('1.00',{}).get('percent_val','0'), minority_state.get('2.00',{}).get('percent_val','0'),minority_nation.get('3.00',{}).get('percent_val','0'),minority_nation.get('4.00',{}).get('percent_val','0'),minority_nation.get('5.00',{}).get('percent_val','0'),minority_nation.get('6.00',{}).get('percent_val','0')]]))
                    ])
    fig5.update_layout(width=800, height=390,font_size=15,title={'text':'Percentage of schools with students of racial/ethnic minority, <br> in {year}, for the State Program {state_abv}'.format(state_abv=dashboard_filters['state_abv'],year=dashboard_filters['survey_taken_year']),
                                                                 'x':0.5})
    plot_div = plot(fig5, output_type='div', include_plotlyjs=False)
    return plot_div

def table_graph(new_response,heading,headers,y_column):
    headerColor = 'grey'
    fig = go.Figure(data=[go.Table(
    header=dict(
        values=headers,
        line_color='white',
        fill_color=headerColor,
        align=['left','center'],
        font=dict(color='white', size=14)
    ),
    cells=dict(
        values=[
        y_column,
        new_response['state_values'],
        new_response['national_values']],
        line_color='white',
        # 2-D list of colors for alternating rows
        #fill_color = [[rowOddColor,rowEvenColor,rowOddColor, rowEvenColor,rowOddColor]*5],
        align = ['left', 'center'],
        font = dict(color = 'darkslategray', size = 14),
        height=30,  # Adjust the cell height here (in pixels)

        ))
    ])

    fig.update_layout(title=heading, font_size=15,width=700, height=740)
    plot_div = plot(fig, output_type='div', include_plotlyjs=False)
    plot_div = plot_div.replace('<td>', '<td style="padding: 10px;white-space: normal;">')

    return plot_div

def main_query(column_name,filters,key): 
    if key=='state':
        filters=filters
    if key=='all':
        filters=filters.copy()
        if "state_abv" in filters:
            filters.pop('state_abv')
        if "state_abv__in" in filters:
            filters.pop('state_abv__in')
        print('MAIN QUERY',filters)
    data = dict(SchoolDetails.objects.values_list(column_name).filter(**filters).annotate(total = Count(column_name)))
    # print(data)
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
                'parents_of_students_without_idd':'Parents of students without IDD','school_psychologist':'School Psychologist/ Counselor/ Social Worker','special_olympics_state_program_staff':'SO state staff'}
    state_values= [] 
    national_values=[]
    y_axis=['Special Education Teachers','Students without IDD','Student with IDD','School Administrators','General Education Teachers','Physical Education (PE) Teachers ',
            'Athletic Director','Adapted PE teachers','Parents of Students with IDD','Parents of Students without IDD','Psychologist/ Counselor/ Social Worker','Special Olympics State Program Staff']

    for key in yes_response.keys():
        state_values.append(response[key]['state'].get('1',{}).get('percent_val',0))
        national_values.append(response[key]['national'].get('1',{}).get('percent_val',0))
    new_response = {'state_values':state_values,'national_values':national_values,'lables':y_axis} #Main response to go out of this functions
    title='Frequency of Leadership Team membership <br> among common types of participants'
    state_name = (dashboard_filters["state_abv"]) + ' ' +str(dashboard_filters['survey_taken_year']) + " %"
    headers=['Participant',state_name,'National %']
    
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
         'table_titles': {
            'table1': "Characteristics of schools locale",
            'table2': "Characteristics of schools level",
            'table3': "Percentage of schools at each student enrollment level",
            'table4': "Percentage of schools with students receiving free or reduced-price lunch",
            'table5': "Percentage of schools with students of racial/ethnic minority",
            'table6': "Frequency of Leadership Team membership among common types of participants",
        }
    }
    return context

@login_required(login_url='../auth/login')
def tables(request):
    state = CustomUser.objects.values('state').filter(username=request.user)[0]
    state=state.get('state','None')
    print("NEW STATE", state)
    if request.method=='GET':
        filter_state = state
        if state=='all':
            filter_state = 'AK'# on inital load some data has to be displayed so defaulting to ma
        print("TABLES 0", state)

        context = load_dashboard(dashboard_filters={'state_abv':filter_state,'survey_taken_year':'2023'},dropdown=Filters(state=state_choices(state)))
      
    if request.method=='POST':
        state = state_choices(state)
        post_data = request.POST.copy()  # Make a mutable copy of the POST data
        post_data['school_county'] = 'all'
        print("TABLES 1", state)
        dropdown = Filters(state,post_data)
        print(dropdown)
        if dropdown.is_valid():

            dashboard_filters = dropdown.cleaned_data
            context = load_dashboard(dashboard_filters,dropdown)
            
    return render(request, 'analytics/index_table.html', context)          
