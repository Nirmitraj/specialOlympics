from django.shortcuts import render
from plotly.offline import plot
import plotly.graph_objects as go
from django.db.models import Sum,Count
from analytics.models import SchoolDetails
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
    