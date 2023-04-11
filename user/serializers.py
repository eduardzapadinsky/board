from rest_framework import serializers

from .models import UserModel


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user

    """

    class Meta:
        model = UserModel
        fields = '__all__'
