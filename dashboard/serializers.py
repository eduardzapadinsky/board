from rest_framework import serializers
from .models import Card


class CardSerializer(serializers.ModelSerializer):
    """
    Serializer for card

    """

    class Meta:
        model = Card
        fields = "__all__"
        read_only_fields = ["id", "created", "updated", "is_deleted", "creator"]
