from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password

from .models import UserModel


class RegistrationForm(forms.Form):
    """
    Form for registration

    """

    username = forms.CharField(max_length=20, required=True, label="Username",
                               widget=forms.TextInput(attrs={
                                   "class": "form-control",
                                   "placeholder": "Username"
                               }))
    first_name = forms.CharField(max_length=20, label="First name",
                                 widget=forms.TextInput(attrs={
                                     "class": "form-control",
                                     "placeholder": "First Name"
                                 }))
    email = forms.EmailField(validators=[validate_email], required=True, max_length=100, label="Email",
                             widget=forms.EmailInput(attrs={
                                 "class": "form-control",
                                 "placeholder": "Email"
                             }))
    password = forms.CharField(validators=[validate_password], max_length=128, required=True, label="Password",
                               widget=forms.PasswordInput(attrs={
                                   "class": "form-control",
                                   "placeholder": "Password"
                               }))

    class Meta:
        model = UserModel
        fields = ["username", "first_name", "email", "password"]

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            UserModel.objects.get(username=username)
            raise ValidationError("username exists")
        except UserModel.DoesNotExist:
            return username

    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            UserModel.objects.get(email=email)
            raise ValidationError("email exists")
        except UserModel.DoesNotExist:
            return email


class LoginForm(forms.Form):
    """
    Form for login

    """

    username = forms.CharField(label="Username", required=True,
                               widget=forms.TextInput(attrs={
                                   "class": "form-control",
                                   "placeholder": "First Name"
                               }))
    password = forms.CharField(label="Password", required=True,
                               widget=forms.PasswordInput(attrs={
                                   "class": "form-control",
                                   "placeholder": "Password"
                               }))
