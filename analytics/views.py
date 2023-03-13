from django.shortcuts import render
from plotly.offline import plot
import plotly.graph_objects as go
from django.db.models import Sum,Count
from analytics.models import SchoolDetails
from sklearn import preprocessing
import numpy as np
#print(SchoolDetails.objects.values('school_state','survey_taken').annotate(total = Count('survey_taken')))

def surveys(request):
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
    
    def scatter_2():
        x1 = [1,2,3,4]
        y1 = [30, 35, 25, 80]

        trace = go.Scatter(
            x=x1,
            y = y1
        )
        layout = dict(
            title='Simple Graph',
            xaxis=dict(range=[min(x1), max(x1)]),
            yaxis = dict(range=[min(y1), max(y1)])
        )

        fig = go.Figure(data=[trace], layout=layout)
        plot_div = plot(fig, output_type='div', include_plotlyjs=False)
        return plot_div

    context ={
        'plot1': bar(),
        #'plot2': scatter_2()
    }

    return render(request, 'analytics/welcome.html', context)
    
def tables(request):
    def school_locale_data(state_abv=None):
        if not state_abv:
            return  SchoolDetails.objects.values_list('locale')
        if state_abv:
            return SchoolDetails.objects.filter(state_abv='MA').values_list('locale')
 
    def school_level_data(state_abv=None):
        if not state_abv:
            data= SchoolDetails.objects.values_list('gradeLevel_WithPreschool').annotate(total = Count('implementation_level'))
        if state_abv:
            data = SchoolDetails.objects.values_list('gradeLevel_WithPreschool').filter(state_abv='MA').annotate(total = Count('implementation_level'))
        return {str(key):val for key,val in data}
    
    def school_student_enrollment_range(state_abv=None):
        if not state_abv:
            data= SchoolDetails.objects.values_list('student_enrollment_range').annotate(total = Count('student_enrollment_range'))
        if state_abv:
            data = SchoolDetails.objects.values_list('student_enrollment_range').filter(state_abv='MA').annotate(total = Count('student_enrollment_range'))
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

    def school_locale_graph():
        locale_data = school_locale_data(state_abv='MA')
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

        fig1.update_layout(width=900, height=450,title='Characteristics of schoolslocale in 2022, as reported by NCES',)
        plot_div = plot(fig1, output_type='div', include_plotlyjs=False)
        return plot_div
    
    def school_level_graph():
        school_level = school_level_data(state_abv='MA')
        national_level = school_level_data()
        school_level=percentage_values(school_level)
        national_level=percentage_values(national_level)
        print(school_level,national_level)
        fig2 = go.Figure(data=[go.Table(header=dict(values=['School level', 'State 2022 year %','National 2022 year %']),
                        cells=dict(values=[['Elementary','Middle','High','Other','Preschool'], 
                                            [school_level['Elementary']['percent_val'], school_level['Middle']['percent_val'], school_level['High']['percent_val'], school_level['Other']['percent_val'],school_level['Preschool']['percent_val']],
                                            [national_level['Elementary']['percent_val'],national_level['Middle']['percent_val'],national_level['High']['percent_val'],national_level['Other']['percent_val'],national_level['Preschool']['percent_val']]]))
                            ])

        fig2.update_layout(width=900, height=450,title='Characteristics of schools level in 2022, as reported by NCES',)
        plot_div = plot(fig2, output_type='div', include_plotlyjs=False)
        return plot_div
    
    def school_student_enrollment():
        student_enroll_state = school_student_enrollment_range(state_abv='MA')
        student_enroll_nation = school_student_enrollment_range()
        student_enroll_state=percentage_values(student_enroll_state)
        student_enroll_nation=percentage_values(student_enroll_nation)
        print(student_enroll_state,student_enroll_nation)
        fig3 = go.Figure(data=[go.Table(header=dict(values=['Student enrollment', 'State 2022 year %','National 2022 year %']),
                        cells=dict(values=[['< 500','501-1000','1001-1500','More than 1500'], 
                                           [student_enroll_state['<500']['percent_val'], student_enroll_state['501-1000']['percent_val'], student_enroll_state['1001-1500']['percent_val'], student_enroll_state['>1500']['percent_val']],
                                           [student_enroll_nation['<500']['percent_val'], student_enroll_nation['501-1000']['percent_val'], student_enroll_nation['1001-1500']['percent_val'], student_enroll_nation['>1500']['percent_val']],
]))
                            ])
#{'None': {'value': 0, 
# 'percent_val': 0.0}, 
# '777.00': {'value': 4, 'percent_val': 2.7}, 
# '501-1000': {'value': 59, 'percent_val': 39.9}, 
# '<500': {'value': 42, 'percent_val': 28.4}, 
# '>1500': {'value': 16, 'percent_val': 10.8}, 
# '1001-1500': {'value': 27, 'percent_val': 18.2}}
        fig3.update_layout(width=900, height=450,title='Characteristics of school_student_enrollment in 2022, as reported by NCES',)
        plot_div = plot(fig3, output_type='div', include_plotlyjs=False)
        return plot_div

    context ={
        'table_plot_1':school_locale_graph(),
        'table_plot_2':school_level_graph(),
        'table_plot_3':school_student_enrollment()
    }
    return render(request,'analytics/tables.html',context)