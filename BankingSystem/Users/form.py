from django import forms
from .models import Individual

class UpdateUserForm(forms.Form):
    username = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(max_length=100, required=False)
    password = forms.CharField(max_length=100, required=False)

class UpdatePersonalDetailsForm(UpdateUserForm):
    message = forms.CharField(
        widget=forms.Textarea(),
        max_length=1000,
        help_text='The max length of the text is 1000.'
    )
    class Meta:
        model = Individual
        fields = ['user', 'phoneNumber', 'mailingAddress']