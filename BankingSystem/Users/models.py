from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from djmoney.models.fields import MoneyField
from django.core.validators import RegexValidator
from localflavor.us.models import USSocialSecurityNumberField


class BankUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # 'ADMIN', 'TIER2', 'TIER1', 'CUSTOMER', 'MERCHANT'
    user_type = models.CharField(max_length=10)

    # 'ACTIVE', 'INACTIVE'
    state = models.CharField(max_length=10)

    # personal info
    email = models.EmailField()
    phone_regex = RegexValidator(regex=r'^\+?1?\d{10}$')
    phone = models.CharField(validators=[phone_regex], max_length=12, blank=True)  # validators should be a list
    address = models.CharField(max_length=200)

    # deposit
    debit_balance = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')
    checking_balance = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')
    saving_balance = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')


class Request(models.Model):
    user = models.ForeignKey(User)

    # create date
    created = models.DateTimeField()

    # 'FUND', 'PAYMENT', 'ACCOUNT_OPEN', 'ACCOUNT_UPDATE'
    request = models.CharField(max_length=20)

    # permission
    # 3, 2, 1, 0 = ADMIN, TIER2, TIER1, Individuals/Merchants
    permission = models.IntegerField()

    # ----- ACCOUNT related -----
    # 'ADMIN', 'TIER2', 'TIER1', 'CUSTOMER', 'MERCHANT'
    user_type = models.CharField(max_length=10)

    # personal info
    email = models.EmailField()
    phone_regex = RegexValidator(regex=r'^\+?1?\d{10}$')
    phone = models.CharField(validators=[phone_regex], max_length=12, blank=True)  # validators should be a list
    address = models.CharField(max_length=200)
    password = models.CharField(max_length=200)

    # ----- PAYMENT related -----

    # ----- FUND related -----

