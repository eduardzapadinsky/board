from django import forms

from .models import Card


class CardForm(forms.ModelForm):
    """
    Form for card

    """

    class Meta:
        model = Card
        fields = ["description", "executor"]

