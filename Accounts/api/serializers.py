from django.contrib.auth import get_user_model
from rest_framework import serializers
from job.models import Job

User = get_user_model()

    
class UserSerializer(serializers.ModelSerializer):

    job_detail = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = [
            'phonenumber',
            'password',
            'email',
            'first_name',
            'last_name',
            'job',
            'job_detail',
        ]
        extra_kwargs = {
            'password': {'write_only':True, 'min_length': 5},
            'job_detail': {'read_only':True},
        }
    
    def get_job_detail(self, obj) -> dict:
        if obj.job:
            return {
                'occupation': obj.job.occupation,
                'description': obj.job.description,
            }
        return None

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)    
        user = super().update(instance, validated_data)  

        if password:
            user.set_password(password)    
            user.save()

        return user

class RequestOTPSerializer(serializers.Serializer):
    phonenumber = serializers.CharField()

class VerifyOTPSerializer(serializers.Serializer):
    phonenumber = serializers.CharField()
    otp = serializers.CharField()

class TokenPairSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()

class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()
