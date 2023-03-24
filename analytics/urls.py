from django.urls import path
from analytics import views
from analytics.dash_apps.finished_apps import surveys_taken,surveys_dup

urlpatterns=[
    path('',views.index,name='surveys_taken'),
    path('tables.html',views.tables,name='tables data'),
    path('welcome.html',views.index,name='surveys_taken'),
    path('filter_welcome/',views.dropdown,name='dropdown'),
    path('filter_tables/',views.dropdown,name='dropdown'),
]