from django.shortcuts import render
from plotly.offline import plot
import plotly.graph_objects as go
import plotly.express as px
from django.http import HttpResponseRedirect
from django.db.models import Sum,Count
from .forms import StateForm
from analytics.models import SchoolDetails
import pandas as pd

#print(SchoolDetails.objects.values('school_state','survey_taken').annotate(total = Count('survey_taken')))

def dropdown(request):
    if request.method=='POST':
        f = StateForm(request.POST)
        print('FORM:',f)
       # print("CLEANED DATA:",f.cleaned_data['state_abv'])
       # print('FORM:',f.is_valid())
        if f.is_valid():
            print("CLEANED DATA:",f.cleaned_data['state_abv'])
            return HttpResponseRedirect('tables.html')
    if request.method=='GET':
        f=StateForm()
    return render(request, 'analytics/tables.html', {'form':f})

def get_states(request):
    states = list(SchoolDetails.objects.values_list('school_state').distinct())
    context = {"posts": states}
    print(context)
    return render(request, "analytics/tables.html", context)

def surveys(request):
    def core_experience_data(key,state_abv_=None):
        select_names = {'sports':'unified_sports_component',
                        'leadership':'youth_leadership_component',
                        'whole_school':'whole_school_component'}
        if key:
            data = dict(SchoolDetails.objects.values_list(select_names[key]).filter(state_abv='MA').annotate(total = Count(select_names[key])))
            data = data.get(True,0) #considering only partipated people
            return data
        else:
            return 0
        
        
    def bar():
        school_surveys=SchoolDetails.objects.values('school_state','survey_taken').annotate(total = Count('survey_taken')).order_by('school_state')
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
            title='school_surveys',
            yaxis = dict(range=[min(survey_true), max(survey_true)]),
            barmode='group'
        )

        fig = go.Figure(data=trace, layout=layout)
        plot_div = plot(fig, output_type='div', include_plotlyjs=False)
        return plot_div
    
    def pie(state_abv=None):
        sports=core_experience_data('sports')
        leadership = core_experience_data('leadership')
        wholeschool = core_experience_data('whole_school')

        print(sports,leadership,wholeschool)
        core_exp_df = pd.DataFrame(dict(
            lables = ['sports','leadership','wholeschool'],
            values = [sports,leadership,wholeschool]
        ))

        fig = px.pie(core_exp_df, values='values', names='lables',title='Core experience implementation in 2022 {state_abv}'.format(state_abv='MA'))
        plot_div = plot(fig, output_type='div', include_plotlyjs=False)
        return plot_div
    context ={
        'plot1': bar(),
        'plot2': pie()
    }

    return render(request, 'analytics/welcome.html', context)
    
def tables(request):

    def school_locale_data(state_abv_=None):
        if not state_abv_:
            return  SchoolDetails.objects.values_list('locale')
        if state_abv_:
            return SchoolDetails.objects.filter(state_abv='MA').values_list('locale')
 
    def school_level_data(state_abv_=None):
        keys = ['Elementary','Middle','High','Other','Preschool']
        if not state_abv_:
            data= dict(SchoolDetails.objects.values_list('gradeLevel_WithPreschool').annotate(total = Count('implementation_level')))
        if state_abv_:
            data = dict(SchoolDetails.objects.values_list('gradeLevel_WithPreschool').filter(state_abv='MA').annotate(total = Count('implementation_level')))
        for val in keys:
            if val not in data.keys():
                data[val]=0
        print("LOGGER:",data)
        return data #{str(key):val for key,val in data}
    
    def school_enrollment_data(state_abv_=None):
        if not state_abv_:
            data= SchoolDetails.objects.values_list('student_enrollment_range').annotate(total = Count('student_enrollment_range'))
        if state_abv_:
            data = SchoolDetails.objects.values_list('student_enrollment_range').filter(state_abv='MA').annotate(total = Count('student_enrollment_range'))
        return {str(key):val for key,val in data}
    
    def school_lunch_data(state_abv_=None):
        if not state_abv_:
            data= SchoolDetails.objects.values_list('student_free_reduced_lunch').annotate(total = Count('student_free_reduced_lunch'))
        if state_abv_:
            data = SchoolDetails.objects.values_list('student_free_reduced_lunch').filter(state_abv='MA').annotate(total = Count('student_free_reduced_lunch'))
        return {str(key):val for key,val in data}
    
    def school_minority_data(state_abv_=None):
        if not state_abv_:
            data= SchoolDetails.objects.values_list('student_nonwhite_population').annotate(total = Count('student_nonwhite_population'))
        if state_abv_:
            data = SchoolDetails.objects.values_list('student_nonwhite_population').filter(state_abv='MA').annotate(total = Count('student_nonwhite_population'))
        return {str(key):val for key,val in data} 
    

    def percentage_values(total_values):
        if type(total_values) == list:
            values = total_values
            return [round(((i/sum(values))*100),2) for i in values]
        
        elif type(total_values) == dict:
            data = list(total_values.values())
            percent_arr=[round(((i/sum(data))*100),1) for i in data ] 
            res = {key:{'value':total_values[key],'percent_val':percent_arr[i]} for i,key in enumerate(total_values.keys()) }
            return res

    def school_locale_graph(state_abv_=None):
        locale_data = school_locale_data(state_abv_='MA')
        locale_statecount={}
        for val in locale_data:
            sub_text = val[0].split(':')[0]
            if sub_text not in locale_statecount.keys():
                locale_statecount[sub_text] = 0
            locale_statecount[sub_text] +=1
        print(locale_statecount)
        locale_state = percentage_values(locale_statecount)
        total_locale_data=school_locale_data()
        locale_nationcount={}

        for val in total_locale_data:
            sub_text = val[0].split(':')[0]
            if sub_text not in locale_nationcount.keys():
                locale_nationcount[sub_text] = 0
            locale_nationcount[sub_text] +=1
        print(locale_nationcount)
        locale_nation = percentage_values(locale_nationcount)
        print(locale_state,locale_nation)

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

        fig1.update_layout(width=700, height=350,title='Characteristics of schoolslocale in 2022, for the state {state_abv}'.format(state_abv=state_abv_))
        plot_div = plot(fig1, output_type='div', include_plotlyjs=False)
        return plot_div
    
    def school_level_graph(state_abv_=None):
        school_level = school_level_data(state_abv_='MA')
        national_level = school_level_data()
        school_level=percentage_values(school_level)
        national_level=percentage_values(national_level)
        print('School level',school_level,national_level)
        fig2 = go.Figure(data=[go.Table(header=dict(values=['School level', 'State 2022 year %','National 2022 year %']),
                        cells=dict(values=[['Elementary','Middle','High','Other','Preschool'], 
                                            [school_level['Elementary']['percent_val'], school_level['Middle']['percent_val'], school_level['High']['percent_val'], school_level['Other']['percent_val'],school_level['Preschool']['percent_val']],
                                            [national_level['Elementary']['percent_val'],national_level['Middle']['percent_val'],national_level['High']['percent_val'],national_level['Other']['percent_val'],national_level['Preschool']['percent_val']]]))
                            ])

        fig2.update_layout(width=700, height=350,title='Characteristics of schools level in 2022, for the state {state_abv}'.format(state_abv=state_abv_))
        plot_div = plot(fig2, output_type='div', include_plotlyjs=False)
        return plot_div
    
    def school_student_enrollment(state_abv_=None):
        student_enroll_state = school_enrollment_data(state_abv_='MA')
        student_enroll_nation = school_enrollment_data()
        student_enroll_state = percentage_values(student_enroll_state)
        student_enroll_nation = percentage_values(student_enroll_nation)
        print(student_enroll_state,student_enroll_nation)
        fig3 = go.Figure(data=[go.Table(header=dict(values=['Student enrollment', 'State 2022 year %','National 2022 year %']),
                        cells=dict(values=[['< 500','501-1000','1001-1500','More than 1500'], 
                                           [student_enroll_state['<500']['percent_val'], student_enroll_state['501-1000']['percent_val'], student_enroll_state['1001-1500']['percent_val'], student_enroll_state['>1500']['percent_val']],
                                           [student_enroll_nation['<500']['percent_val'], student_enroll_nation['501-1000']['percent_val'], student_enroll_nation['1001-1500']['percent_val'], student_enroll_nation['>1500']['percent_val']],]))])

        fig3.update_layout(width=700, height=350,title='Characteristics of school_student_enrollment in 2022, for the state {state_abv}'.format(state_abv=state_abv_))
        plot_div = plot(fig3, output_type='div', include_plotlyjs=False)
        return plot_div

    def school_free_reduce_lunch(state_abv_=None):
        student_lunch_state = school_lunch_data(state_abv_='MA')
        student_lunch_nation = school_lunch_data()
        student_lunch_state=percentage_values(student_lunch_state)
        student_lunch_nation=percentage_values(student_lunch_nation)
        print('school_free_reduce_lunch:',student_lunch_state,student_lunch_nation)
        fig4 = go.Figure(data=[go.Table(header=dict(values=['Student Receiving free or reduced lunch%', 'State 2022 year %','National 2022 year %']),
                        cells=dict(values=[['0-25','26-50','51-75','76-100'], 
                                           [student_lunch_state.get("0%-25%",{}).get('percent_val','Nill'),student_lunch_state.get("26%-50%",{}).get('percent_val','Nill'), student_lunch_state.get("51%-75%",{}).get('percent_val','Nill'), student_lunch_state.get("76%-100%",{}).get('percent_val','Nill')],
                                           [student_lunch_nation.get("0%-25%",{}).get('percent_val','Nill'),student_lunch_nation.get("26%-50%",{}).get('percent_val','Nill'), student_lunch_nation.get("51%-75%",{}).get('percent_val','Nill'), student_lunch_nation.get("76%-100%",{}).get('percent_val','Nill')]]))
                            ])
        fig4.update_layout(width=700, height=350,title='Characteristics of school free reduced lunch in 2022, for the state {state_abv}'.format(state_abv=state_abv_))
        plot_div = plot(fig4, output_type='div', include_plotlyjs=False)
        return plot_div
    
    def school_minority(state_abv_=None):
        minority_state = school_minority_data(state_abv_='MA')
        minority_nation = school_minority_data()
        minority_state=percentage_values(minority_state)
        minority_nation=percentage_values(minority_nation)
        print('student_minority:',minority_state,minority_nation)
        fig5 = go.Figure(data=[go.Table(header=dict(values=['Students of racial/ethnic minority %', 'State 2022 year %','National 2022 year %']),
                 cells=dict(values=[['< 10','11-25','26-50','51-75','76-90','> 90'], 
                                    [minority_state.get('10% or less',{}).get('percent_val','Nill'), minority_state.get('11%-25%',{}).get('percent_val','Nill'), minority_state.get('26%-50%',{}).get('percent_val','Nill'), minority_state.get('51%-75%',{}).get('percent_val','Nill'), minority_state.get('76%-90%',{}).get('percent_val','Nill'),minority_state.get('More than 90%',{}).get('percent_val','Nill')],
                                    [minority_nation.get('10% or less',{}).get('percent_val','Nill'), minority_state.get('11%-25%',{}).get('percent_val','Nill'),minority_nation.get('26%-50%',{}).get('percent_val','Nill'),minority_nation.get('51%-75%',{}).get('percent_val','Nill'),minority_nation.get('76%-90%',{}).get('percent_val','Nill'),minority_nation.get('More than 90%',{}).get('percent_val','Nill')]]))
                     ])
        fig5.update_layout(width=800, height=370,title='Characteristics of Students of racial/ethnic minority in 2022, for the state {state_abv}'.format(state_abv=state_abv_))
        plot_div = plot(fig5, output_type='div', include_plotlyjs=False)
        return plot_div
    

    def get_states():
        states = list(SchoolDetails.objects.values_list('school_state').distinct())
        lis=[]
        for state in states:
            lis.append(state[0])
        #context = {"states": states}
        #print(context)
        return lis
        # return render(request, "analytics/tables.html", context)

    def dropdown(request):
        if request.method=='POST':
            f = StateForm(request.POST)
            print('FORM:',f)
            if f.is_valid():
                print("CLEANED DATA:",f.cleaned_data['state_abv'])
                return HttpResponseRedirect('tables.html')
        if request.method=='GET':
            f=StateForm()
        return render(request, 'analytics/tables.html', {'form':f})

    context ={
        'table_plot_1':school_locale_graph(),
        'table_plot_2':school_level_graph(),
        'table_plot_3':school_student_enrollment(),
        'table_plot_4':school_free_reduce_lunch(),
        'table_plot_5':school_minority(),
        'states':get_states()
    }
    return render(request,'analytics/tables.html',context)