from django import forms

from .models import Card


class CardForm(forms.ModelForm):
    """
    Form for card

    """

    class Meta:
        model = Card
        fields = ["description"]


class CardFormSuperuser(forms.ModelForm):
    """
    Form for card for superuser

    """

    class Meta:
        model = Card
        fields = ["description", "executor"]
