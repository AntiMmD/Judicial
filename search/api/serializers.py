from rest_framework import serializers

from Laws.models import Law


# def clean_highlight(text):
#     import re

#     if not text:
#         return text

#     text = text.replace("&nbsp;", " ")
#     text = re.sub(r'[\r\n\t]+', ' ', text)
#     text = re.sub(r'\s{2,}', ' ', text)
#     text = re.sub(r'\s*(</?b>)\s*', r'\1', text)

#     return text.strip()

class SearchResultSerializer(serializers.ModelSerializer):
    # parent_title = serializers.SerializerMethodField()
    # relevance = serializers.IntegerField(read_only=True)
    
    brief_main_content = serializers.SerializerMethodField()

    class Meta:
        model = Law
        fields = [
            "id",
            "slug",
            "type",
            "title",
            # "short_summary",
            # "summary",
            "brief_main_content",
            "article_no",
            "note_no",
            "priority",
            "legal_type",
            # "parent",
            # "parent_title",
            # "relevance",
        ]

    # def get_parent_title(self, obj) -> str | None:
    #     parent = obj.parent
    #     if parent is None:
    #         return None
    #     return parent.title

    def get_brief_main_content(self, obj):
        highlighted = getattr(obj, "highlighted_content", None)
        if highlighted:
            # highlighted = clean_highlight(highlighted)
            return highlighted
        return (obj.main_content or "")[:300]
    


# class SearchFacetsSerializer(serializers.Serializer):
#     Law = serializers.IntegerField(required=False, default=0)
#     Article = serializers.IntegerField(required=False, default=0)
#     Note = serializers.IntegerField(required=False, default=0)


class SearchResponseSerializer(serializers.Serializer):
    query = serializers.CharField(allow_blank=True)
    type_filter = serializers.CharField(allow_null=True)
    legal_type_filter = serializers.CharField(allow_null=True)
    # facets = SearchFacetsSerializer()
    count = serializers.IntegerField()
    next = serializers.CharField(allow_null=True)
    previous = serializers.CharField(allow_null=True)
    results = SearchResultSerializer(many=True)
