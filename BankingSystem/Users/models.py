from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import RegexValidator
from localflavor.us.models import USSocialSecurityNumberField


class BankUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # 'ADMIN', 'TIER2', 'TIER1', 'CUSTOMER', 'MERCHANT'
    user_type = models.CharField(max_length=10)

    # 'ACTIVE', 'INACTIVE'
    state = models.CharField(max_length=10)

    # personal info
    username = models.CharField(max_length=200)
    email = models.EmailField()
    phone_regex = RegexValidator(regex=r'^\+?1?\d{10}$')
    phone = models.CharField(validators=[phone_regex], max_length=12, blank=True)  # validators should be a list
    address = models.CharField(max_length=200)

    # deposit
    credit_balance = models.DecimalField(max_digits=10, decimal_places=2)
    checking_balance = models.DecimalField(max_digits=10, decimal_places=2)
    saving_balance = models.DecimalField(max_digits=10, decimal_places=2)

    # credit
    credit_number = models.CharField(max_length=16)
    cvv = models.CharField(max_length=3)


class Request(models.Model):
    # from to
    from_id = models.IntegerField()
    to_id = models.IntegerField()

    # create date
    created = models.DateTimeField()

    # state 'PENDING', 'APPROVED', 'DECLINED'
    state = models.CharField(max_length=20)

    # sub-state for T1, 'WAITING_T2', 'WAITING_T2_EX', 'WAITING_EX', 'WAITING'
    sub_state = models.CharField(max_length=20)

    # 'FUND', 'PAYMENT', 'ACCOUNT_OPEN', 'ACCOUNT_UPDATE', 'APPROVE_REQUEST', 'CREDIT_PAYMENT'
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
    increment_credit_balance = models.DecimalField(max_digits=10, decimal_places=2)
    increment_checking_balance = models.DecimalField(max_digits=10, decimal_places=2)
    increment_saving_balance = models.DecimalField(max_digits=10, decimal_places=2)

    # ----- PAYMENT/FUND related -----
    critical = models.IntegerField()
    money = models.DecimalField(max_digits=10, decimal_places=2)
    from_balance = models.CharField(max_length=20)
    to_balance = models.CharField(max_length=20)

    credit_number = models.CharField(max_length=16)
    cvv = models.CharField(max_length=3)

    # ----- APPROVE REQUEST related -----
    request_id = models.IntegerField()


class Log(models.Model):

    # create date
    created = models.DateTimeField()

    # msg
    msg = models.CharField(max_length=100)


