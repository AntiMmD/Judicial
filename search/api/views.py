from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from search.api.pagination import SearchPagination
from search.api.serializers import SearchResponseSerializer, SearchResultSerializer
from search.services import VALID_CATEGORIES, VALID_TYPES, search_laws


class LawSearchView(APIView):
    pagination_class = SearchPagination

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="q",
                type=str,
                location=OpenApiParameter.QUERY,
                description="عبارت جستجو. در صورت خالی بودن، نتایج بر اساس اولویت مرتب می‌شوند.",
            ),
            OpenApiParameter(
                name="type",
                type=str,
                location=OpenApiParameter.QUERY,
                enum=list(VALID_TYPES),
                description="فیلتر نوع: Law یا Article . در صورت عدم ارسال، همه انواع برگردانده می‌شوند.",
            ),
            OpenApiParameter(
                name="category",
                type=str,
                location=OpenApiParameter.QUERY,
                enum=list(VALID_CATEGORIES),
                description="فیلتر دسته‌بندی قانون (مثلاً Regulation، Bylaw و ...).",
            ),
            OpenApiParameter(
                name="page",
                type=int,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="page_size",
                type=int,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="search_in_title",
                type=bool,
                location=OpenApiParameter.QUERY,
                description="جستجو در عنوان. پیش‌فرض: true",
            ),
            OpenApiParameter(
                name="search_in_content",
                type=bool,
                location=OpenApiParameter.QUERY,
                description="جستجو در متن اصلی. پیش‌فرض: true",
            ),
        ],
        responses={
            200: SearchResponseSerializer,
            400: OpenApiResponse(description="پارامتر نامعتبر."),
        },
        description=(
            "جستجو در قوانین، مواد و تبصره‌ها. "
            "بدون فیلتر type همه انواع نمایش داده می‌شوند؛ "
            "با انتخاب type، جستجو فقط در همان نوع انجام می‌شود. "
        ),
    )
    def get(self, request):
        query = request.query_params.get("q", "").strip() or None
        type_filter = request.query_params.get("type", "").strip() or None
        category_filter = request.query_params.get("category", "").strip() or None
        search_in_title:bool = request.query_params.get("category", "").strip() or None
        search_in_content:bool = request.query_params.get("category", "").strip() or None
        
        if type_filter and type_filter not in VALID_TYPES:
            return Response(
                {
                    "detail": f"نوع نامعتبر. مقادیر مجاز: {', '.join(sorted(VALID_TYPES))}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if category_filter and category_filter not in VALID_CATEGORIES:
            return Response(
                {
                    "detail": f"دسته‌بندی نامعتبر. مقادیر مجاز: {', '.join(sorted(VALID_CATEGORIES))}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        results_qs = search_laws(
            query,
            type_filter=type_filter,
            category_filter=category_filter,
            # search_in_title=search_in_title,
            # search_in_content=search_in_content
        )
            

        paginator = self.pagination_class()
        paginated_results = paginator.paginate_queryset(results_qs, request, view=self)


        payload = {
            "query": query,
            "type_filter": type_filter,
            "category_filter": category_filter,
            "count": paginator.page.paginator.count,
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
            "results": SearchResultSerializer(paginated_results, many=True).data,
        }

        return Response(payload, status=status.HTTP_200_OK)
    





# class LawSearchView(APIView):
#     pagination_class = SearchPagination

#     @extend_schema(
#         parameters=[
#             OpenApiParameter(
#                 name="q",
#                 type=str,
#                 location=OpenApiParameter.QUERY,
#                 description="عبارت جستجو. در صورت خالی بودن، نتایج بر اساس اولویت مرتب می‌شوند.",
#             ),
#             OpenApiParameter(
#                 name="type",
#                 type=str,
#                 location=OpenApiParameter.QUERY,
#                 enum=list(VALID_TYPES),
#                 description="فیلتر نوع: Law، Article یا Note. در صورت عدم ارسال، همه انواع برگردانده می‌شوند.",
#             ),
#             OpenApiParameter(
#                 name="category",
#                 type=str,
#                 location=OpenApiParameter.QUERY,
#                 enum=list(VALID_CATEGORIES),
#                 description="فیلتر دسته‌بندی قانون (مثلاً Regulation، Bylaw و ...).",
#             ),
#             OpenApiParameter(
#                 name="page",
#                 type=int,
#                 location=OpenApiParameter.QUERY,
#             ),
#             OpenApiParameter(
#                 name="page_size",
#                 type=int,
#                 location=OpenApiParameter.QUERY,
#             ),
#         ],
#         responses={
#             200: SearchResponseSerializer,
#             400: OpenApiResponse(description="پارامتر نامعتبر."),
#         },
#         description=(
#             "جستجو در قوانین، مواد و تبصره‌ها. "
#             "بدون فیلتر type همه انواع نمایش داده می‌شوند؛ "
#             "با انتخاب type، جستجو فقط در همان نوع انجام می‌شود. "
#             "فیلد facets تعداد نتایج هر نوع را برای همان عبارت جستجو نشان می‌دهد."
#         ),
#     )
#     def get(self, request):
#         query = request.query_params.get("q", "").strip()
#         type_filter = request.query_params.get("type", "").strip() or None
#         category_filter = request.query_params.get("category", "").strip() or None

#         if type_filter and type_filter not in VALID_TYPES:
#             return Response(
#                 {
#                     "detail": f"نوع نامعتبر. مقادیر مجاز: {', '.join(sorted(VALID_TYPES))}"
#                 },
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         if category_filter and category_filter not in VALID_CATEGORIES:
#             return Response(
#                 {
#                     "detail": f"دسته‌بندی نامعتبر. مقادیر مجاز: {', '.join(sorted(VALID_CATEGORIES))}"
#                 },
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         results_qs, facets = search_laws(
#             query,
#             type_filter=type_filter,
#             category_filter=category_filter,
#         )

#         results_qs = results_qs.select_related("parent")

#         paginator = self.pagination_class()
#         paginated_results = paginator.paginate_queryset(results_qs, request, view=self)

#         normalized_facets = {type_name: facets.get(type_name, 0) for type_name in VALID_TYPES}

#         payload = {
#             "query": query,
#             "type_filter": type_filter,
#             "category_filter": category_filter,
#             "facets": normalized_facets,
#             "count": paginator.page.paginator.count,
#             "next": paginator.get_next_link(),
#             "previous": paginator.get_previous_link(),
#             "results": SearchResultSerializer(paginated_results, many=True).data,
#         }

#         return Response(payload, status=status.HTTP_200_OK)
