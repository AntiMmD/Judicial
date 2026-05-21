from django.contrib import admin
from django.urls import path
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('', include('Documents.urls')),
    path('admin/', admin.site.urls),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='api_schema'), name='api_docs'),
    path('api/schema/', SpectacularAPIView.as_view(), name='api_schema'),
    path('api/auth/', include('Accounts.urls')),
    path('api/jobs/', include('job.urls')),
    path("api/quiz/", include("quiz.urls")),
]

