from django import forms
from .models import Employee
from django.contrib.auth.models import User

class UpdatePersonalDetailsForm(forms.Form):
    username = forms.CharField(label='User Name', max_length=100)
    phone_number = forms.CharField(label='Phone Number', max_length=100)
    email = forms.CharField(label='Email Address', max_length=100)
    mail_address = forms.CharField(label='Mailing Address', widget=forms.Textarea, max_length=4000)