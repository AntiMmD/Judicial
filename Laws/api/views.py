from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from Laws.api.serializers import LawSerializer
from Laws.models import Law

# Law here means type="Law"
class GetLaw(APIView):
    # slug is only intended for SEO
    @extend_schema(
        responses={200: LawSerializer},
        description="Fetches a Law by ID, including all its related Articles and Notes as children."
    )
    def get(self, request, pk, slug=None):
        law = get_object_or_404(Law, pk=pk)

        serializer = LawSerializer(law)
        return Response(serializer.data, status=status.HTTP_200_OK)