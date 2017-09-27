from django import forms


class GetSystemLogForm(forms.Form):
    rows = forms.IntegerField(max_value=100, required=True)
