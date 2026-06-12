from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiExample,
    OpenApiParameter,
    OpenApiTypes,
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import AllowAny

from Advisory_Opinions.models import AdvisoryOpinion
from Advisory_Opinions.api.serializers import AdvisoryOpinionSeriailizer, AdvisoryOpinionListSeriailizer
from Advisory_Opinions.api.pagination import opinionPagination


class OpinionListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = AdvisoryOpinionListSeriailizer
    queryset = AdvisoryOpinion.objects.all()
    pagination_class = opinionPagination
    
class GetopinionView(APIView):
    def get(self, request, pk, slug=None):
        try:
            opinion = AdvisoryOpinion.objects.get(pk=pk)

        except AdvisoryOpinion.DoesNotExist:
            return Response({"detail": "نظریه مشورتی یافت نشد."}, status=status.HTTP_404_NOT_FOUND)
        
        data = AdvisoryOpinionSeriailizer(opinion).data
        return Response(data, status=status.HTTP_200_OK)
    

# class GetopinionView(generics.RetrieveAPIView):
#     permission_classes = [AllowAny]
#     serializer_class = AdvisoryOpinionSeriailizer
#     queryset = AdvisoryOpinion.objects.all()


        