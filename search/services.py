from django.db.models import Case, Count, IntegerField, Q, Value, When

from Laws.models import Law

SEARCHABLE_FIELDS = (
    "title",
    "short_summary",
    "summary",
    "main_content",
    "code",
    "approving_authority",
)

RELEVANCE_WEIGHTS = {
    "title": 10,
    "short_summary": 6,
    "summary": 4,
    "main_content": 2,
    "code": 5,
    "approving_authority": 3,
}

VALID_TYPES = {choice.value for choice in Law.LegalType}
VALID_CATEGORIES = {choice.value for choice in Law.Category}


def _build_text_filter(query: str) -> Q:
    text_filter = Q()
    for field in SEARCHABLE_FIELDS:
        text_filter |= Q(**{f"{field}__icontains": query})
    return text_filter


def _annotate_relevance(queryset, query: str):
    score_parts = []
    for field, weight in RELEVANCE_WEIGHTS.items():
        score_parts.append(
            Case(
                When(**{f"{field}__icontains": query}, then=Value(weight)),
                default=Value(0),
                output_field=IntegerField(),
            )
        )

    relevance = score_parts[0]
    for part in score_parts[1:]:
        relevance = relevance + part

    return queryset.annotate(relevance=relevance)


def search_laws(
    query: str,
    *,
    type_filter: str | None = None,
    category_filter: str | None = None,
):
    """
    Search Law records with optional type/category filters.

    Returns (results_queryset, facets_dict) where facets show per-type counts
    for the current query (ignoring type_filter so the client can switch tabs).
    """
    base_qs = Law.objects.all()

    if category_filter:
        base_qs = base_qs.filter(category=category_filter)

    if query:
        base_qs = base_qs.filter(_build_text_filter(query))
        base_qs = _annotate_relevance(base_qs, query)
        ordering = ("-relevance", "-priority", "-views")
    else:
        base_qs = base_qs.annotate(relevance=Value(0, output_field=IntegerField()))
        ordering = ("-priority", "-views")

    facets = {
        row["type"]: row["count"]
        for row in base_qs.values("type").annotate(count=Count("id"))
    }

    results_qs = base_qs
    if type_filter:
        results_qs = results_qs.filter(type=type_filter)

    return results_qs.order_by(*ordering), facets
