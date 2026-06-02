from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from Laws.api.serializers import (
    LawListSerializer,
    LawDetailSerializer,
    LawChildSerializer,
    LawDetailWithChildrenSerializer,
    ArticleDetailSerializer,
    ArticleDetailWithNotesSerializer,
)
from Laws.models import Law
from Laws.api.pagination import LawListPagination, LawChildrenPagination

class LawsListView(generics.ListAPIView):
    queryset = Law.objects.filter(type=Law.LegalType.law).order_by("-priority")
    serializer_class = LawListSerializer
    pagination_class = LawListPagination

class ArticlesListView(generics.ListAPIView):
    queryset = Law.objects.filter(type=Law.LegalType.article).order_by("-priority")
    serializer_class = LawListSerializer
    pagination_class = LawListPagination

class CategoriesListView(APIView):
    @extend_schema(
        responses={
            200: OpenApiResponse(
                response=list[str],
                examples=[
                    OpenApiExample(
                        "Categories list",
                        value=[
                            "Law",
                            "Agreement",
                            "Approval",
                            "Bylaw",
                            "Charter",
                            "Circular",
                            "Convention",
                            "Instruction",
                            "Procedure",
                            "Regulation",
                            "Statutes",
                        ],
                    )
                ],
            )
        }
    )
    def get(self, request, *args, **kwargs):
        return Response(Law.Category.values,status=status.HTTP_200_OK)

    
# Law here means type="Law"
class GetLawView(APIView):
    @extend_schema(
        responses={
            200: LawDetailWithChildrenSerializer ,
            400: OpenApiResponse(description="Object exists but is not of type Law."),
            404: OpenApiResponse(description="Law not found."),
        },
        description="Fetches a Law by ID, including all its related Articles and Notes as children."
    )
    # slug is only intended for SEO
    def get(self, request, pk, slug=None):
        try:
            law = Law.objects.get(pk=pk)
        except Law.DoesNotExist:
            return Response(
                {"detail": "قانون یافت نشد."},
                status=status.HTTP_404_NOT_FOUND
            )

        if law.type != Law.LegalType.law:
            return Response(
                {"detail": "This endpoint is only intended for fetching Laws"},
                status=status.HTTP_400_BAD_REQUEST
            )

        children_qs = Law.objects.filter(parent=law).order_by("article_no", "type", "note_no")

        paginator = LawChildrenPagination()
        paginated_children = paginator.paginate_queryset(children_qs, request, view=self)

        law_data = LawDetailSerializer(law).data
        law_data["children"] = paginator.get_paginated_response(
            LawChildSerializer (paginated_children, many=True).data
        ).data

        return Response(law_data, status=status.HTTP_200_OK)


class GetArticleView(APIView):
    @extend_schema(
        responses={
            200: ArticleDetailWithNotesSerializer,
            400: OpenApiResponse(description="Object exists but is not of type Article."),
            404: OpenApiResponse(description="Article not found."),
        },
        description="Fetches an Article by ID, including all its related Notes as children."
    )
    def get(self, request, pk, slug=None):
        try:
            article = Law.objects.get(pk=pk)
        except Law.DoesNotExist:
            return Response({"detail": "ماده یافت نشد."}, status=status.HTTP_404_NOT_FOUND)

        if article.type != Law.LegalType.article:
            return Response(
                {"detail": "This endpoint is only intended for fetching Articles"},
                status=status.HTTP_400_BAD_REQUEST
            )

        notes_qs = Law.objects.filter(
            parent=article.parent,
            type=Law.LegalType.note,
            article_no=article.article_no,
        ).order_by("note_no")

        paginator = LawChildrenPagination()
        paginated_notes = paginator.paginate_queryset(notes_qs, request, view=self)

        article_data = ArticleDetailSerializer(article).data
        article_data["notes"] = paginator.get_paginated_response(
            LawChildSerializer(paginated_notes, many=True).data
        ).data

        return Response(article_data, status=status.HTTP_200_OK)
