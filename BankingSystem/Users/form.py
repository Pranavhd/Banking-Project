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

    email = forms.EmailField(max_length=100, required=False)
    phone = forms.RegexField(regex=r'^\+?1?\d{10}$', required=False)
    address = forms.CharField(max_length=200, required=False)


class AccountDeleteGetForm(forms.Form):
    id = forms.IntegerField(required=True)


class HandleRequestForm(forms.Form):
    id = forms.IntegerField(required=True)
    approve = forms.IntegerField(min_value=0, max_value=1, required=True)


class ApproveRequestForm(forms.Form):
    to_username = forms.CharField(max_length=100, required=False)
    user_type = forms.CharField(max_length=10, required=True)
    request_id = forms.IntegerField(required=True)


class MakeTransferPostForm(forms.Form):
    to_email = forms.EmailField(required=True)
    money = MoneyField(required=True, min_value=0.01, max_digits=6, decimal_places=2, default_currency='USD')
