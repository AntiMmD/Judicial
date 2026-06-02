from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from Laws.models import Law


class LawListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Law
        fields = ["id", "slug", "title", "priority", "short_summary", "category"]


class LawChildSerializer(serializers.ModelSerializer):
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
            "category",
            "article_count",
            "notes_count",
        ]


class PaginatedLawChildrenSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.CharField(allow_null=True)
    previous = serializers.CharField(allow_null=True)
    results = LawChildSerializer(many=True)


class LawDetailSerializer(serializers.ModelSerializer):
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
            "category",
        ]


# Documentation-only (view attaches real value)
class LawDetailWithChildrenSerializer(LawDetailSerializer):
    children = serializers.SerializerMethodField()

    class Meta(LawDetailSerializer.Meta):
        fields = LawDetailSerializer.Meta.fields + ["children"]

    @extend_schema_field(PaginatedLawChildrenSerializer)
    def get_children(self, obj):
        return None


class ArticleDetailSerializer(serializers.ModelSerializer):
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
            "category",
            "parent",
        ]

# Documentation-only (view attaches real value)
class ArticleDetailWithNotesSerializer(ArticleDetailSerializer):
    notes = serializers.SerializerMethodField()

    class Meta(ArticleDetailSerializer.Meta):
        fields = ArticleDetailSerializer.Meta.fields + ["notes"]

    @extend_schema_field(PaginatedLawChildrenSerializer)
    def get_notes(self, obj):
        return None
