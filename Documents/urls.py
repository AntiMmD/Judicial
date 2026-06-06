from django.urls import path
from .views import index, job_api, accounts_api, search_api, setup_guide, project_structure

app_name = 'documents'

urlpatterns = [
    path('', index, name='index'),
    path('setup/', setup_guide, name='setup'),
    path('structure/', project_structure, name='structure'),
    path('accounts/', accounts_api, name='accounts'),
    path('job/', job_api, name='job'),
    path('search/', search_api, name='search'),

]

