from django.urls import path
from analytics import views,tables,index_graph, index_table, get_counties
from authenticate import views as auth_views
from analytics.dash_apps.finished_apps import surveys_taken,surveys_dup
from django.urls import path
from django_select2.views import AutoResponseView
from analytics import feedback
from analytics import pdf_view

dashboard_filters={'state_abv':'sca','survey_taken_year':2023}
urlpatterns=[
    path('',auth_views.home,name='home'),
    path('tables/',tables.tables,name='tables'),
    path('dashboard/',views.index,name='dashboard'),
    path('index_graph/',index_graph.index,name='index_graph'),
    path('api/get_graph/', index_graph.get_graph, name='get_graph'),
    path('get_counties/', index_graph.get_counties, name='get_counties'),
    path('select2/', AutoResponseView.as_view(), name='select2'),
    path('feedback/', feedback.feedback, name='feedback'),

    path('pdf/', pdf_view.PdfView.as_view(), name='pdf_view'),

    path('index_table/',index_table.tables,name='index_table'),
    path('download_pdf/', index_graph.download_pdf, name='download_pdf'),


    # path('welcome.html/',views.index,name='homepage'),
    # path('tables.html/',tables.tables,name='tablespage'),
]