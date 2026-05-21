from django.contrib.auth import get_user_model
from rest_framework.pagination import PageNumberPagination
User = get_user_model()



class UserPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = "page_size"
    max_page_size = 100




class UserSerializerForAdmins(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'phonenumber',
            'password',
            'first_name',
            'last_name', 
            'role',
            'national_code',
            'birthday_date',
            'is_active',
            'is_staff',
        ]
        extra_kwargs = {
            'password': {'write_only':True, 'min_length': 5},
            'id': {'read_only':True},
        }

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