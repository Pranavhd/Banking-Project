from django import forms


class CreateUserForm(forms.Form):
    username = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(max_length=100, required=True)
    password = forms.CharField(max_length=100, required=True)
    level = forms.IntegerField(required=True, min_value=0, max_value=2)

