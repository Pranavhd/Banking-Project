from django import forms
from .models import Individual

class UpdatePersonalDetailsForm(forms.Form):

    username = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(max_length=100, required=True)
    mailing_address = forms.CharField(widget=forms.Textarea(), max_length=4000)
    class Meta:
        model = Individual
        fields = ['username', 'email', 'phone_number', 'mailing_address']