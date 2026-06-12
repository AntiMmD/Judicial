from django.contrib.postgres.search import SearchQuery, SearchHeadline


from Laws.models import Law

VALID_TYPES = {
    'Law',
    'Article',
}
VALID_CATEGORIES = {choice.value for choice in Law.LegalType}

def search_laws(query: str, *, type_filter: str | None = None, legal_type_filter: str | None = None):
    qs = Law.objects.all()

    if legal_type_filter:
        qs = qs.filter(legal_type=legal_type_filter)

    if query:
        search_query = SearchQuery(query, search_type="plain")

        qs = qs.filter(
            search_vector=search_query
        ).annotate(
            highlighted_content=SearchHeadline(
                "main_content",
                search_query,
                start_sel="<b>",
                stop_sel="</b>",
                max_fragments=1,
                max_words=60,
                min_words=20,
            )
        )

    if type_filter:
        qs = qs.filter(type=type_filter)

    return qs.order_by("-priority", "-views")











# SEARCHABLE_FIELDS = (
#     "title",
#     "short_summary",
#     "summary",
#     "main_content",
#     "code",
#     "approving_authority",
# )

# from django.db.models import Case, Count, IntegerField, Q, Value, When

# from Laws.models import Law

# SEARCHABLE_FIELDS = (
#     "title",
#     "short_summary",
#     "summary",
#     "main_content",
#     "code",
#     "approving_authority",
# )

# RELEVANCE_WEIGHTS = {
#     "title": 10,
#     "short_summary": 6,
#     "summary": 4,
#     "main_content": 2,
#     "code": 5,
#     "approving_authority": 3,
# }

# VALID_TYPES = {choice.value for choice in Law.LegalType}
# VALID_CATEGORIES = {choice.value for choice in Law.legal_type}


# def _build_text_filter(query: str) -> Q:
#     text_filter = Q()
#     for field in SEARCHABLE_FIELDS:
#         text_filter |= Q(**{f"{field}__icontains": query})
#     return text_filter


# def _annotate_relevance(queryset, query: str):
#     score_parts = []
#     for field, weight in RELEVANCE_WEIGHTS.items():
#         score_parts.append(
#             Case(
#                 When(**{f"{field}__icontains": query}, then=Value(weight)),
#                 default=Value(0),
#                 output_field=IntegerField(),
#             )
#         )

#     relevance = score_parts[0]
#     for part in score_parts[1:]:
#         relevance = relevance + part

#     return queryset.annotate(relevance=relevance)


# def search_laws(
#     query: str,
#     *,
#     type_filter: str | None = None,
#     legal_type_filter: str | None = None,
# ):
#     """
#     Search Law records with optional type/legal_type filters.

#     Returns (results_queryset, facets_dict) where facets show per-type counts
#     for the current query (ignoring type_filter so the client can switch tabs).
#     """
#     qs = Law.objects.all()

#     if legal_type_filter:
#         qs = qs.filter(legal_type=legal_type_filter)

#     if query:
#         qs = qs.filter(_build_text_filter(query))
#         qs = _annotate_relevance(qs, query)
#         ordering = ("-relevance", "-priority", "-views")
#     else:
#         qs = qs.annotate(relevance=Value(0, output_field=IntegerField()))
#         ordering = ("-priority", "-views")

#     facets = {
#         row["type"]: row["count"]
#         for row in qs.values("type").annotate(count=Count("id"))
#     }

#     results_qs = qs
#     if type_filter:
#         results_qs = results_qs.filter(type=type_filter)

#     return results_qs.order_by(*ordering), facets
