from django.urls import path
from analytics import views
from analytics.dash_apps.finished_apps import surveys_taken,surveys_dup

urlpatterns=[
    path('',views.surveys,name='surveys_taken'),
    path('tables.html',views.tables,name='surveys_taken'),
]