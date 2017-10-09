from django import forms
from .models import Individual
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField

class UpdatePersonalDetailsForm(forms.Form):
    username = forms.CharField(label='User Name', max_length=100)
    phone_number = PhoneNumberField()
    email = forms.EmailField(help_text='A valid email address, please.')
    mail_address = forms.CharField(label='Mailing Address', widget=forms.Textarea, max_length=4000)
