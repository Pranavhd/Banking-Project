from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from . import form
from . import models


# login
def login_view(request):
    context = {}
    return render(request, 'login.html', context)


def login_post_view(request):
    context = {}
    return render(request, 'logout.html', context)


def logout_view(request):
    context = {}
    return render(request, 'logout.html', context)


# admin
def admin_view(request):
    context = {}
    return render(request, 'admin.html', context)


# tier1
def tier1_view(request):
    context = {}
    return render(request, 'tier1.html', context)


# tier2
def tier2_view(request):
    context = {}
    return render(request, 'tier2.html', context)


# customer
def customer_view(request):
    context = {}
    return render(request, 'customer.html', context)


# merchant
def merchant_view(request):
    context = {}
    return render(request, 'merchant.html', context)


