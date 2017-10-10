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
        context = {'msg': 'not post'}
        return render(request, 'error.html', context, status=400)

    # check format of POST data
    f = form.LoginForm(request.POST)
    if not f.is_valid():
        context = {'msg': 'not valid post data'}
        return render(request, 'error.html', context, status=400)

    # login by using 'username' & password
    user = authenticate(username=request.POST['username'], password=request.POST['password'])
    if user is None:
        context = {'msg': 'not valid user or password'}
        return render(request, 'error.html', context, status=401)
    login(request, user)

    # redirect bank user
    bank_user = models.BankUser.objects.get(user=user)
    if bank_user.user_type == 'ADMIN':
        return redirect('/admin/')
    elif bank_user.user_type == 'TIER1':
        return redirect('/tier1/')
    elif bank_user.user_type == 'TIER2':
        return redirect('/tier2/')
    elif bank_user.user_type == 'CUSTOMER':
        return redirect('/customer/')
    elif bank_user.user_type == 'MERCHANT':
        return redirect('/merchant/')
    else:
        return redirect('/logout/')


def logout_view(request):
    context = {}
    logout(request)
    return render(request, 'logout.html', context)


# signup
def signup_view(request):
    context = {}
    return render(request, 'signup.html', context)


def signup_post_view(request):
    # not pos data
    if request.method != "POST":
        context = {'msg': 'not post'}
        return render(request, 'error.html', context, status=400)

    # check format of POST data
    f = form.SignupForm(request.POST)
    if not f.is_valid():
        context = {'msg': 'not valid post data'}
        return render(request, 'error.html', context, status=400)
    if request.POST['user_type'] not in ['ADMIN', 'TIER2', 'TIER1', 'CUSTOMER', 'MERCHANT']:
        context = {'msg': 'not valid user type'}
        return render(request, 'error.html', context, status=400)

    # create user
    user = User.objects.create_user(
        username=request.POST['username'],
        password=request.POST['password'],
        email=request.POST['email']
    )
    models.BankUser.objects.create(user=user, user_type=request.POST['user_type'])

    context = {'msg': 'user created'}
    return render(request, 'success.html', context)


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


