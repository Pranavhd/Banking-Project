from django import forms
from .models import Employee
from django.contrib.auth.models import User

class UpdatePersonalDetailsForm(forms.Form):
    #User.username = forms.CharField(max_length=100, required=True)
    #User.email = forms.EmailField(max_length=100, required=False)
    #mail_address = forms.CharField(widget=forms.Textarea(), max_length=4000)

    class Meta:
        model = Employee
        fields = ['username', 'email', 'mail_address']