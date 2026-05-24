from job.api.serializers import JobSerializer
from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from drf_spectacular.utils import extend_schema, OpenApiExample
from job.models import Job

class ManageJobView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = JobSerializer
    queryset = Job.objects.all()

class JobListView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = JobSerializer
    queryset = Job.objects.all()

