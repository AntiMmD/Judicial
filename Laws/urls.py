from django.urls import path
from Laws.api.views import GetLaw, GetArticle

urlpatterns = [
    # type: articles
    path('articles/<slug>/<pk>', GetArticle.as_view(), name='slug-article-detail'),
    path('articles/<pk>', GetArticle.as_view(), name='id-article-detail'),

    # type: laws
    path('<slug>/<pk>', GetLaw.as_view(), name='slug-law-detail'),
    path('<pk>', GetLaw.as_view(), name='id-law-detail'),
]
