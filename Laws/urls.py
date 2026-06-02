from django.urls import path
from Laws.api.views import GetLaw

urlpatterns = [
    path('<slug>/<pk>', GetLaw.as_view(), name='slug-get-law'),
    path('<pk>', GetLaw.as_view(), name='id-law-detail'),
]