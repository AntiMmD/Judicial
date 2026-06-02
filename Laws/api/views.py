from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from Laws.api.serializers import LawSerializer, ArticleSerializer
from Laws.models import Law

# Law here means type="Law"
class GetLaw(APIView):
    @extend_schema(
        responses={
            200: LawSerializer,
            400: OpenApiResponse(description="Object exists but is not of type Law."),
            404: OpenApiResponse(description="Law not found."),
        },
        description="Fetches a Law by ID, including all its related Articles and Notes as children."
    )
    # slug is only intended for SEO
    def get(self, request, pk, slug=None):
        try:
            law = Law.objects.get(pk=pk)
            if law.type == Law.LegalType.law:
                serializer = LawSerializer(law)
                return Response(serializer.data, status=status.HTTP_200_OK)
        
            return Response(
                {"detail": "This endpoint is only intended for fetching Laws"},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Law.DoesNotExist:
            return Response(
            {"detail": "قانون یافت نشد."},
            status=status.HTTP_404_NOT_FOUND
        )

    

class GetArticle(APIView):
    @extend_schema(
        responses={
            200: ArticleSerializer,
            400: OpenApiResponse(description="Object exists but is not of type Article."),
            404: OpenApiResponse(description="Article not found."),
        },
        description="Fetches an Article by ID, including all its related Notes as children."
    )
    # slug is only intended for SEO
    def get(self, request, pk, slug=None):
        try:
            article = Law.objects.get(pk=pk)
            if article.type == Law.LegalType.article:
                serializer = ArticleSerializer(article)
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            return Response(
                {"detail": "This endpoint is only intended for fetching Articles"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except Law.DoesNotExist:
            return Response(
            {"detail": "ماده یافت نشد."},
            status=status.HTTP_404_NOT_FOUND
            )
