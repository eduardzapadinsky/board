from rest_framework import serializers
from .models import Card


class CardSerializer(serializers.ModelSerializer):
    """
    Serializer for post
    """

    class Meta:
        model = Card
        fields = "__all__"
        read_only_fields = ["created", "updated"]
