from django.urls import path
from analytics import views,tables
from analytics.dash_apps.finished_apps import surveys_taken,surveys_dup
dashboard_filters={'state_abv':'sca','survey_taken_year':2022}
urlpatterns=[
    path('',views.index,name='dashboard'),
    path('tables/',tables.tables,name='tables data'),
    path('dashboard/',views.index,name='surveys_taken'),
    path('welcome.html/',views.index,name='homepage'),
    path('tables.html/',tables.tables,name='tablespage'),
]