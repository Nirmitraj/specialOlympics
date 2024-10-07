from django.urls import path
from analytics import admin_password_change, views,tables,index_graph, index_table, list_users
from authenticate import views as auth_views
from analytics.dash_apps.finished_apps import surveys_taken,surveys_dup
from django.urls import path
from django_select2.views import AutoResponseView
from analytics import feedback
from django.conf.urls.static import static
from django.conf import settings


dashboard_filters={'state_abv':'sca','survey_taken_year':2023}
urlpatterns=[
    path('',auth_views.home,name='home'),
    # path('tables/',tables.tables,name='tables'),
    path('dashboard/',index_graph.index,name='dashboard'),
    path('index_graph/',index_graph.index,name='index_graph'),
    path('api/get_graph/', index_graph.get_graph, name='get_graph'),
    path('get_counties/', index_graph.get_counties, name='get_counties'),
    path('select2/', AutoResponseView.as_view(), name='select2'),
    path('feedback/', feedback.feedback, name='feedback'),


    path('index_table/',index_table.tables,name='index_table'),
    path('receive_graph_images/', index_graph.receive_graph_images, name='receive_graph_images'),

    path('list_users/', list_users.list_users, name='list_users'),
    path('admin_password_change/', admin_password_change.admin_password_change, name='admin_password_change'),

    # path('welcome.html/',views.index,name='homepage'),
    # path('tables.html/',tables.tables,name='tablespage'),
    path('upload/', views.upload, name = 'upload'),
    # path('upload-document/', views.upload_document, name='upload_document'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
