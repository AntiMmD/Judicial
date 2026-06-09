from django.urls import path
from Laws.api.views import GetLawView, LawsListView, CategoriesListView

urlpatterns = [
    
    path('categories/', CategoriesListView.as_view(), name='categories-list'),
    path('<slug>/<pk>', GetLawView.as_view(), name='slug-law-detail'),
    path('<pk>', GetLawView.as_view(), name='id-law-detail'),
    path('', LawsListView.as_view(), name= 'laws-list'),
]
