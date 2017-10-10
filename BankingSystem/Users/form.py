from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, required=True)
    password = forms.CharField(max_length=100, required=True)


class SignupForm(forms.Form):

    username = forms.CharField(max_length=100, required=True)
    password = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(help_text='A valid email address, please.')

    user_type = forms.CharField(max_length=10, required=True)
