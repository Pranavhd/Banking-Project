from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from BankingSystem.Accounts import models as accountInfo

# Create your views here.
# defining view for getting personal details information
def credit_limit_increase_view(request):
    user = User.objects.first()  # TODO: get the currently logged in user
    credit_info = accountInfo.objects.get(user=user)


