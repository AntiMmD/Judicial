from django.urls import path
import job.api.views


app_name = 'job'

urlpatterns = [
    path('create/', job.api.views.CreateJobView.as_view(), name='create'),
    path('<int:pk>/', job.api.views.ManageJobView.as_view(), name='job'),
    path('', job.api.views.DisplayJobListView.as_view(), name='list'),    
]