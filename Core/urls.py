from django.contrib import admin
from django.urls import path
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='api_schema'), name='api_docs'),
    path('schema/', SpectacularAPIView.as_view(), name='api_schema'),
    path('auth/', include('Accounts.urls')),
    path('jobs/', include('job.urls')),
    path('quiz/', include('quiz.urls')),
    path('laws/search/', include('search.urls')),
    path('laws/', include('Laws.urls')),
    path('', include('Documents.urls')),
]

