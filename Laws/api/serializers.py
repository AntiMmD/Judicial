from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from Laws.models import Law


class LawListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Law
        fields = ["id", "slug", "type", "title", "priority", "short_summary", "legal_type"]


class LawChildSerializer(serializers.ModelSerializer):
    breadcrumbs_titles= serializers.SerializerMethodField()

    class Meta:
        model = Law
        fields = [
            "id",
            "slug",
            "type",
            "article_no",
            "note_no",
            "title",
            "short_summary",
            "summary",
            "main_content",
            "main_source",
            "date",
            "priority",
            "legal_type",
            "article_count",
            "notes_count",
            "breadcrumbs_titles",
        ]

    def get_breadcrumbs_titles(self, obj):
        return list(
            obj.breadcrumbs.values_list("title", flat=True)
        )

class BreadcrumbGroupSerializer(serializers.Serializer):
    breadcrumbs_title = serializers.ListField(
        child=serializers.CharField()
    )
    items = LawChildSerializer(many=True)


class PaginatedLawChildrenSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.CharField(allow_null=True)
    previous = serializers.CharField(allow_null=True)
    results = BreadcrumbGroupSerializer(many=True)


class LawDetailSerializer(serializers.ModelSerializer):
    breadcrumbs_titles= serializers.SerializerMethodField()

    class Meta:
        model = Law
        fields = [
            "id",
            "slug",
            "type",
            "article_count",
            "notes_count",
            "title",
            "approving_authority",
            "short_summary",
            "summary",
            "main_content",
            "main_source",
            "date",
            "priority",
            "legal_type",
            "breadcrumbs_titles",
        ]

    def get_breadcrumbs_titles(self, obj):
        return list(
            obj.breadcrumbs.values_list("title", flat=True)
        )


# Documentation-only (view attaches real value)
class LawDetailWithChildrenSerializer(LawDetailSerializer):
    children = serializers.SerializerMethodField()

    class Meta(LawDetailSerializer.Meta):
        fields = LawDetailSerializer.Meta.fields + ["children"]

    @extend_schema_field(PaginatedLawChildrenSerializer)
    def get_children(self, obj):
        return None


class ArticleDetailSerializer(serializers.ModelSerializer):
    breadcrumbs_titles= serializers.SerializerMethodField()

    class Meta:
        model = Law
        fields = [
            "id",
            "slug",
            "type",
            "notes_count",
            "title",
            "short_summary",
            "summary",
            "main_content",
            "main_source",
            "date",
            "priority",
            "legal_type",
            "parent",
            "breadcrumbs_titles",
        ]

    def get_breadcrumbs_titles(self, obj):
        return list(
            obj.breadcrumbs.values_list("title", flat=True)
        )

# Documentation-only (view attaches real value)
class ArticleDetailWithNotesSerializer(ArticleDetailSerializer):
    notes = serializers.SerializerMethodField()

    class Meta(ArticleDetailSerializer.Meta):
        fields = ArticleDetailSerializer.Meta.fields + ["notes"]

    @extend_schema_field(PaginatedLawChildrenSerializer)
    def get_notes(self, obj):
        return None
