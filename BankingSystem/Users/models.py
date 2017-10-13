from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from djmoney.models.fields import MoneyField


# Create your models here.
class BankUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # 'ADMIN', 'TIER2', 'TIER1', 'CUSTOMER', 'MERCHANT'
    user_type = models.CharField(max_length=10)

    # personal info
    ssn = models.CharField(max_length=10)
    phone = PhoneNumberField(blank=False)

    # deposit
    debit_balance = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')
    checking_balance = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')
    saving_balance = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')
