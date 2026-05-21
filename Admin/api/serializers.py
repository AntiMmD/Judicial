from django.contrib.auth import get_user_model
from rest_framework import serializers
from job.models import Job

User = get_user_model()

class UserSerializerForAdmins(serializers.ModelSerializer):
    job = serializers.PrimaryKeyRelatedField(
        queryset=Job.objects.all(),
        allow_null=True,
        required=False,
        help_text="Optional. Job ID associated with the user. Can be null."
    )

    job_detail = serializers.SerializerMethodField()
    class Meta:
        model = User

        fields = [
            'phonenumber',
            'password',
            'email',
            'first_name',
            'last_name',
            'role',
            'job',
            'job_detail',
            'is_staff',
            'is_active'
        ]
        extra_kwargs = {
            'password': {'write_only':True, 'min_length': 5},
            'id': {'read_only':True},
        }

    def get_job_detail(self, obj):
        if obj.job:
            return {
                "occupation": obj.job.occupation,
                'description': obj.job.description,
                'is_active': obj.job.is_active,
            }
        return None
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    
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
