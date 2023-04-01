from django import forms

from user.models import UserModel
from .models import Card


# class CardForm(forms.Form):
class CardForm(forms.ModelForm):
    """
    Form for card

    """
    #
    # def __init__(self, *args, **kwargs):
    #     self.user = kwargs.pop("user", None)
    #     super(CardForm, self).__init__(*args, **kwargs)
    #     try:
    #         user_id = self.user.id
    #         print("try")
    #     except Exception:
    #         user_id = 1
    #         print("except")
    #     print("final")
    #     self.fields["executor"].queryset = UserModel.objects.filter(id=user_id)
    #     # self.fields["executor"].queryset = UserModel.objects.filter(id=self.user.id)

    class Meta:
        model = Card
        fields = ["description"]
    # class Meta:
    #     model = Card
    #     fields = ["description", "executor"]


class CardFormSuperuser(forms.ModelForm):
    """
    Form for card for superuser

    """

    class Meta:
        model = Card
        fields = ["description", "executor"]

