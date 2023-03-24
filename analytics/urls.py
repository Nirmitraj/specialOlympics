from django.urls import path
from analytics import views
from analytics.dash_apps.finished_apps import surveys_taken,surveys_dup

urlpatterns=[
    path('',views.surveys,name='surveys_taken'),
    path('tables.html',views.tables,name='tables data'),
    path('index.html',views.surveys,name='surveys_taken'),
    path('state_dropdown/',views.dropdown,name='dropdown'),
]