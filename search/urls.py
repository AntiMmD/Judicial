from django.urls import path

from search.api.views import LawSearchView

app_name = "search"

urlpatterns = [
    path("", LawSearchView.as_view(), name="law-search"),
]
