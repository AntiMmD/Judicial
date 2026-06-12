from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiExample,
    OpenApiParameter,
    OpenApiTypes,
)
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

from collections import defaultdict

class LawsListView(generics.ListAPIView):
    queryset = Law.objects.filter(type=Law.LegalType.law).order_by("-priority")
    serializer_class = LawListSerializer
    pagination_class = LawListPagination

class LegalTypesListView(APIView):
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
        return Response(Law.LegalType.values,status=status.HTTP_200_OK)

    
# Law here means type="Law"
class GetLawView(APIView):

    def _build_children_response(self, request, parent_obj, children_qs, parent_serializer):
        paginator = LawChildrenPagination()
        paginated_children = paginator.paginate_queryset(children_qs, request, view=self)

        parent_data = parent_serializer(parent_obj).data
        children_data = LawChildSerializer(paginated_children, many=True).data

        grouped_results = []
        current_key = None
        current_items = []

        for item in children_data:
            key = tuple(item.get("breadcrumbs_titles") or [])
            item.pop("breadcrumbs_titles", None)

            if key != current_key:
                if current_items:
                    grouped_results.append({
                        "breadcrumbs_title": list(current_key),
                        "items": current_items,
                    })

                current_key = key
                current_items = []

            current_items.append(item)

        if current_items:
            grouped_results.append({
                "breadcrumbs_title": list(current_key),
                "items": current_items,
            })

        paginated = paginator.get_paginated_response(grouped_results)
        parent_data["children"] = paginated.data

        return Response(parent_data, status=status.HTTP_200_OK)


    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="page",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Page number for paginated children.",
            ),
            OpenApiParameter(
                name="page_size",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Number of children to return per page. Default= 25",
            ),
        ],
        responses={
            200: LawDetailWithChildrenSerializer,
            404: OpenApiResponse(description="Law not found."),
        },
        description="Fetches a Law by ID, including all its related Articles and Notes as children."
    )
    def get(self, request, pk, slug=None):
        try:
            law = Law.objects.get(pk=pk)
        except Law.DoesNotExist:
            return Response({"detail": "قانون یافت نشد."}, status=status.HTTP_404_NOT_FOUND)

        if law.type == Law.LegalType.law:
            children_qs = (
                Law.objects
                .filter(parent=law)
                .prefetch_related("breadcrumbs")
                .order_by("article_no", "type", "note_no")
            )

            return self._build_children_response(
                request,
                law,
                children_qs,
                LawDetailSerializer
            )

        elif law.type == Law.Types.article:
            notes_qs = (
                Law.objects
                .filter(
                    parent=law.parent,
                    type=Law.Types.note,
                    article_no=law.article_no,
                )
                .prefetch_related("breadcrumbs")
                .order_by("note_no")
            )

            return self._build_children_response(
                request,
                law,
                notes_qs,
                ArticleDetailSerializer
            )
