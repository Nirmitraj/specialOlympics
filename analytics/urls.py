from django.urls import path
from analytics import views
from analytics.dash_apps.finished_apps import surveys_taken,surveys_dup
dashboard_filters={'state_abv':'sca','survey_taken_year':2022}
urlpatterns=[
    path('',views.index,name='surveys_taken'),
    path('tables.html',views.tables,name='tables data'),
    path('dashboard/',views.index,name='surveys_taken'),
    path('filter_welcome/',views.dropdown,name='dropdown'),
    path('filter_tables/',views.dropdown,name='dropdown'),
]