from job.api.serializers import JobSerializer
from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from drf_spectacular.utils import extend_schema, OpenApiExample
from job.models import Job

@extend_schema(
    examples=[
        OpenApiExample(
            "Valid inputs",
            value={
                "occupation": "Engineer",
                "description": "text",
                'is_active':True
                }
        )
    ],
)    
class CreateJobView(generics.CreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = JobSerializer

class ManageJobView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = JobSerializer
    queryset = Job.objects.all()

class DisplayJobListView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = JobSerializer
    queryset = Job.objects.all()

