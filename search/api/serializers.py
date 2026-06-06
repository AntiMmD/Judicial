from rest_framework import serializers

from Laws.models import Law


class SearchResultSerializer(serializers.ModelSerializer):
    parent_title = serializers.SerializerMethodField()
    relevance = serializers.IntegerField(read_only=True)

    class Meta:
        model = Law
        fields = [
            "id",
            "slug",
            "type",
            "title",
            "short_summary",
            "summary",
            "code",
            "article_no",
            "note_no",
            "priority",
            "category",
            "parent",
            "parent_title",
            "relevance",
        ]

    def get_parent_title(self, obj) -> str | None:
        parent = obj.parent
        if parent is None:
            return None
        return parent.title


class SearchFacetsSerializer(serializers.Serializer):
    Law = serializers.IntegerField(required=False, default=0)
    Article = serializers.IntegerField(required=False, default=0)
    Note = serializers.IntegerField(required=False, default=0)


class SearchResponseSerializer(serializers.Serializer):
    query = serializers.CharField(allow_blank=True)
    type_filter = serializers.CharField(allow_null=True)
    category_filter = serializers.CharField(allow_null=True)
    facets = SearchFacetsSerializer()
    count = serializers.IntegerField()
    next = serializers.CharField(allow_null=True)
    previous = serializers.CharField(allow_null=True)
    results = SearchResultSerializer(many=True)
