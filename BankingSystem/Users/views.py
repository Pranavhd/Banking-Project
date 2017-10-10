from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from . import form
from . import models


# login
def login_view(request):
    context = {}
    return render(request, 'login.html', context)


def login_post_view(request):
    # not pos data
    if request.method != "POST":
        return HttpResponse(status=400)

    # check format of login data
    f = form.LoginForm(request.POST)
    if not f.is_valid():
        return HttpResponse(status=400)

    # login by using 'username' & password
    user = authenticate(username=request.POST['username'], password=request.POST['password'])
    if user is None:
        return HttpResponse(status=401)
    login(request, user)

    # redirect bank user
    bank_user = models.BankUser.objects.get(user=user)
    if bank_user.user_type == 'ADMIN':
        redirect('/admin/')
    elif bank_user.user_type == 'TIER1':
        redirect('/tier1/')
    elif bank_user.user_type == 'TIER2':
        redirect('/tier2/')
    elif bank_user.user_type == 'CUSTOMER':
        redirect('/customer/')
    elif bank_user.user_type == 'MERCHANT':
        redirect('/merchant/')
    else:
        redirect('/logout/')


def logout_view(request):
    context = {}
    logout(request)
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


