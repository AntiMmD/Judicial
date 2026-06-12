from django.urls import path

from Advisory_Opinions.api.views import GetopinionView, OpinionListView

app_name = 'advisory_opinion'

urlpatterns = [
    path('<pk>', GetopinionView.as_view(), name= 'get-opinion'),
    path('', OpinionListView.as_view(), name= 'opinions-list'),

    
]


