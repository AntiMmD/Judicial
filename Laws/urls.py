from django.urls import path
from Laws.api.views import GetLawView, GetArticleView, LawsListView, ArticlesListView, CategoriesListView

urlpatterns = [
    # type: articles
    path('articles/<slug>/<pk>', GetArticleView.as_view(), name='slug-article-detail'),
    path('articles/<pk>', GetArticleView.as_view(), name='id-article-detail'),
    path('articles/', ArticlesListView.as_view(), name= 'articles-list'),

    # type: laws
    path('categories/', CategoriesListView.as_view(), name='categories-list'),
    path('<slug>/<pk>', GetLawView.as_view(), name='slug-law-detail'),
    path('<pk>', GetLawView.as_view(), name='id-law-detail'),
    path('', LawsListView.as_view(), name= 'laws-list'),
]
