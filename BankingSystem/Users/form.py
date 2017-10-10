from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, required=True)
    password = forms.CharField(max_length=100, required=True)


class UpdateUserForm(forms.Form):
    username = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(max_length=100, required=False)
    password = forms.CharField(max_length=100, required=False)


class DeleteUserForm(forms.Form):
    username = forms.CharField(max_length=100, required=True)

