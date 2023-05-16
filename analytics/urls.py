from django.urls import path
from analytics import views,tables
from authenticate import views as auth_views
from analytics.dash_apps.finished_apps import surveys_taken,surveys_dup
dashboard_filters={'state_abv':'sca','survey_taken_year':2022}
urlpatterns=[
    path('',auth_views.home,name='home'),
    path('tables/',tables.tables,name='tables'),
    path('dashboard/',views.index,name='dashboard'),
    # path('welcome.html/',views.index,name='homepage'),
    # path('tables.html/',tables.tables,name='tablespage'),
]