from django import forms
from phonenumber_field.formfields import PhoneNumberField
from djmoney.forms.fields import MoneyField


class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, required=True)
    password = forms.CharField(max_length=100, required=True)


class SignupForm(forms.Form):
    # user
    username = forms.CharField(max_length=100, required=True)
    password = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(max_length=100, required=True)

    # 'ADMIN', 'TIER2', 'TIER1', 'CUSTOMER', 'MERCHANT'
    user_type = forms.CharField(max_length=10, required=True)

    # personal info
    ssn = forms.CharField(max_length=10)
    phone = PhoneNumberField(required=True)


class BackdoorSignupForm(forms.Form):

    username = forms.CharField(max_length=100, required=True)
    password = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(max_length=100, required=True)
    user_type = forms.CharField(max_length=10, required=True)
