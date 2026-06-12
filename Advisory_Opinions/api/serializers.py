from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from Advisory_Opinions.models import AdvisoryOpinion

class AdvisoryOpinionListSeriailizer(serializers.ModelSerializer):
    base_content = serializers.SerializerMethodField()
    summary = serializers.SerializerMethodField()

    class Meta:
        model = AdvisoryOpinion
        fields = [
            'id',
            'slug',
            'summary',
            'base_content',
            'code',
        ]
    
    def get_base_content(self, obj):
        return obj.base_content[150:300]

    def get_summary(self, obj):
        if obj.summary:
            return obj.summary[:200]
        else: return None

class AdvisoryOpinionSeriailizer(serializers.ModelSerializer):
    class Meta:
        model = AdvisoryOpinion
        fields = [
            'id',
            'slug',
            'base_content',
            'main_content',
            'summary',
            'code',
            'main_source',
            'date',
            'views',
            'related_opinions',
            'related_laws'
        ]

