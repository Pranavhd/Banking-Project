from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from djmoney.models.fields import MoneyField


# Create your models here.
class Request(models.Model):
    user = dude = models.ForeignKey(User)

    # create date
    created = models.DateTimeField(null=False, blank=False)

    # 'FUND', 'PAYMENT', 'ACCOUNT_OPEN', 'ACCOUNT_UPDATE'
    request = models.CharField(max_length=20)

    # permission
    # 3, 2, 1, 0 = ADMIN, TIER2, TIER1, Individuals/Merchants
    permission = models.IntegerField()

    # ----- ACCOUNT related -----
    # 'ADMIN', 'TIER2', 'TIER1', 'CUSTOMER', 'MERCHANT'
    user_type = models.CharField(max_length=10)

    # personal info
    ssn = models.CharField(max_length=10)
    phone = PhoneNumberField(blank=False)

    # ----- PAYMENT related -----

    # ----- FUND related -----

