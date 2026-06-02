# Laws/serializers.py
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from Laws.models import Law

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


class LawSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

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
            "parent",
            "children",
        ]
    @extend_schema_field(LawChildSerializer(many=True))
    def get_children(self, obj):
        children = Law.objects.filter(parent=obj).order_by('article_no', 'type', 'note_no')
        return LawChildSerializer(children, many=True).data
    





class ArticleSerializer(serializers.ModelSerializer):
    notes = serializers.SerializerMethodField()

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
            "notes",
        ]
        
    @extend_schema_field(LawChildSerializer(many=True))
    def get_notes(self, obj):
        parent = obj.parent
        notes = Law.objects.filter(
            parent=parent,
            type= Law.LegalType.note,
            article_no= obj.article_no
        )

        return LawChildSerializer(notes, many=True).data