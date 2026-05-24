from django.urls import path
import job.api.views


app_name = 'job'

urlpatterns = [
    path('<int:pk>/', job.api.views.ManageJobView.as_view(), name='manage-job'),
    path('', job.api.views.JobListView.as_view(), name='job-list'),    
]