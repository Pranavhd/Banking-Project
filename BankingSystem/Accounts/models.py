from django.db import models
from django.models.fields import MoneyField
from django.core.exceptions import ValidationError
from Users.models import Profile


class BankingAccount(models.Model):
    account_holder = models.ForeignKey(Profile, on_delete=models.CASCADE)
    account_name = models.CharField(max_length=128)
    funds = MoneyField(max_digits=20, decimal_places=2, default_currency='USD')


class CheckingAccount(BankingAccount):
    None


class SavingsAccount(BankingAccount):
    None


class CreditCard(BankingAccount):
    def validate_length(value, length=19):
        if len(str(value)) != length:
            raise ValidationError("{0} is not the correct length".format(value), code=None, params=None)
    credit_card_number = models.CharField(max_length=19, unique=True, validators=[validate_length])
    ccv_number = models.CharField(max_length=5)
