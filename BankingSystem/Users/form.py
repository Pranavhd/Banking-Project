from django import forms
from phonenumber_field.formfields import PhoneNumberField
from djmoney.forms.fields import MoneyField
from localflavor.us.forms import USSocialSecurityNumberField


class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, required=True)
    password = forms.CharField(max_length=100, required=True)


class AccountOpenForm(forms.Form):
    # user
    username = forms.CharField(max_length=100, required=True)
    password = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(max_length=100, required=True)

    # 'ADMIN', 'TIER2', 'TIER1', 'CUSTOMER', 'MERCHANT'
    user_type = forms.CharField(max_length=10, required=True)

    # personal info
    phone = forms.RegexField(regex=r'^\+?1?\d{10}$')
    address = forms.CharField(max_length=200, required=True)


class AccountUpdateGetForm(forms.Form):
    id = forms.IntegerField(required=True)


class AccountUpdatePostForm(forms.Form):
    id = forms.IntegerField(required=True)

    email = forms.EmailField(max_length=100, required=True)
    phone = forms.RegexField(regex=r'^\+?1?\d{10}$', required=True)
    address = forms.CharField(max_length=200, required=True)


class AccountDeleteGetForm(forms.Form):
    id = forms.IntegerField(required=True)


class HandleRequestForm(forms.Form):
    id = forms.IntegerField(required=True)
    approve = forms.IntegerField(min_value=0, max_value=1, required=True)
