from django.shortcuts import render, redirect
import datetime
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from . import form
from . import models
import collections


# ----- login -----
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

    # check if bank user exist
    try:
        bank_user = models.BankUser.objects.get(user=user)
    except models.BankUser.DoesNotExist:
        context = {'msg': 'no BankUser found'}
        return render(request, 'error.html', context, status=400)

    # redirect
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


# ------ 1. account open -----
def account_open_view(request):
    context = {}
    return render(request, 'account_open.html', context)


def account_open_post_view(request):
    # not pos data
    if request.method != "POST":
        context = {'msg': 'not post'}
        return render(request, 'error.html', context, status=400)

    # check format of POST data
    f = form.AccountOpenForm(request.POST)
    if not f.is_valid():
        context = {'msg': 'not valid post data ' + str(f.errors)}
        return render(request, 'error.html', context, status=400)
    if request.POST['user_type'] not in ['CUSTOMER', 'MERCHANT']:
        context = {'msg': 'not valid user type'}
        return render(request, 'error.html', context, status=400)

    # check if username already exist
    try:
        _ = User.objects.get(username=request.POST['username'])
        context = {'msg': 'username exist'}
        return render(request, 'error.html', context, status=400)
    except User.DoesNotExist:
        pass

    # check phone unique
    try:
        _ = models.BankUser.objects.get(phone=request.POST['phone'])
        context = {'msg': 'phone exist'}
        return render(request, 'error.html', context, status=400)
    except models.BankUser.DoesNotExist:
        pass

    # check email unique
    try:
        _ = models.BankUser.objects.get(email=request.POST['email'])
        context = {'msg': 'email exist'}
        return render(request, 'error.html', context, status=400)
    except models.BankUser.DoesNotExist:
        pass

    # create user
    user = User.objects.create_user(
        username=request.POST['username'],
        password=request.POST['password'],
    )

    # create bank user
    models.BankUser.objects.create(
        user=user,
        state='INACTIVE',
        user_type=request.POST['user_type'],
        username=request.POST['username'],
        phone=request.POST['phone'],
        email=request.POST['email'],
        address=request.POST['address'],
    )

    # create request
    models.Request.objects.create(
        user=user,
        created=datetime.datetime.now(),
        state='PENDING',
        request='ACCOUNT_OPEN',
        permission=0,
        user_type=request.POST['user_type'],
        phone=request.POST['phone'],
        email=request.POST['email'],
        address=request.POST['address'],
    )

    context = {'msg': 'Account Open Request Sent'}
    return render(request, 'success.html', context)


# ------ 2. account update -----
def account_update_view(request):
    context = {}
    return render(request, 'account_update.html', context)


def account_update_post_view(request):
    context = {}
    return render(request, 'success.html', context)


# ------ 3. fund transfer -----
def make_transfer_view(request):
    context = {}
    return render(request, 'make_transfer.html', context)


def make_transfer_post_view(request):
    context = {}
    return render(request, 'success.html', context)


# ------ 4. payment -----
def make_payment_view(request):
    context = {}
    return render(request, 'make_payment.html', context)


def make_payment_post_view(request):
    context = {}
    return render(request, 'success.html', context)


# ----- index -----
def index_view(request):
    if not request.user.is_authenticated():
        return redirect('/login/')

    # check if it is an admin user
    try:
        bank_user = models.BankUser.objects.get(user=request.user)
    except models.BankUser.DoesNotExist:
        context = {'msg': 'not authenticated'}
        return render(request, 'error.html', context, status=401)

    # redirect
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
        return redirect('/login/')


# ----- admin -----
def admin_view(request):
    # check if a valid user
    if not request.user.is_authenticated():
        context = {'msg': 'not authenticated'}
        return render(request, 'error.html', context, status=401)

    # check if it is an admin user
    try:
        bank_user = models.BankUser.objects.get(user=request.user)
    except models.BankUser.DoesNotExist:
        context = {'msg': 'not authenticated'}
        return render(request, 'error.html', context, status=401)
    if bank_user.user_type != 'ADMIN':
        context = {'msg': 'not authenticated'}
        return render(request, 'error.html', context, status=401)

    # render users
    context = {
        'users': [],
        'account_open_requests': [],
        'account_update_requests': [],
        'fund_requests': [],
        'payment_requests': [],
    }
    users = models.BankUser.objects.all().exclude(user_type='ADMIN')
    RenderUser = collections.namedtuple('RenderUser', 'username email phone address')
    for u in users:
        context['users'].append(RenderUser(u.username, u.email, u.phone, u.address))

    # render request
    requests = models.Request.objects.all().exclude(user_type='ADMIN')
    RenderAccountOpenRequest = collections.namedtuple('RenderAccountOpenRequest',
                                                      'username id state created request email phone address ')
    for req in requests:
        # account open
        if req.request == 'ACCOUNT_OPEN':
            context['account_open_requests'].append(RenderAccountOpenRequest(
                req.user.username, req.id, req.state, req.created, req.request, req.email, req.phone, req.address
            ))
        # account update

        # fund

        # payment
    # return HttpResponse(str(context))
    return render(request, 'admin.html', context)


# ----- tier1 -----
def tier1_view(request):
    context = {}
    return render(request, 'tier1.html', context)


# ----- tier2 -----
def tier2_view(request):
    context = {}
    return render(request, 'tier2.html', context)


# ----- customer -----
def customer_view(request):
    context = {}
    return render(request, 'customer.html', context)


# ----- merchant -----
def merchant_view(request):
    context = {}
    return render(request, 'merchant.html', context)


# ----- request ----
def handle_request_post_view(request):

    context = {}

    # check if a valid user
    if not request.user.is_authenticated():
        context = {'msg': 'not authenticated'}
        return render(request, 'error.html', context, status=401)
    try:
        bank_user = models.BankUser.objects.get(user=request.user)
    except models.BankUser.DoesNotExist:
        context = {'msg': 'not authenticated'}
        return render(request, 'error.html', context, status=401)

    # check if a valid request
    f = form.RequestForm(request.POST)
    if not f.is_valid():
        context = {'msg': 'not valid request ' + str(f.errors)}
        return render(request, 'error.html', context, status=400)

    # get request
    try:
        inner_request = models.Request.objects.get(id=request.POST['id'])
    except models.Request.DoesNotExist:
        context = {'msg': 'not valid request '}
        return render(request, 'error.html', context, status=401)
    if inner_request.state != 'PENDING':
        context = {'msg': 'not a pending request '}
        return render(request, 'error.html', context, status=401)

    # ADMIN
    if bank_user.user_type == 'ADMIN':
        # ACCOUNT OPEN
        if inner_request.request == 'ACCOUNT_OPEN':
            if int(request.POST['approve']):
                inner_request.state = 'APPROVED'
                inner_request.save()
                bank_user.state = 'ACTIVE'
                bank_user.save()
                context['msg'] = 'APPROVED'
            else:
                inner_request.state = 'DECLINED'
                inner_request.save()
                context['msg'] = 'DECLINED'

        # ACCOUNT UPDATE
        elif inner_request.request == 'ACCOUNT_UPDATE':
            pass

        # FUND TRANSFER

        # PAYMENT

    elif bank_user.user_type == 'TIER1':
        pass
    elif bank_user.user_type == 'TIER2':
        pass
    elif bank_user.user_type == 'MERCHANT':
        pass
    elif bank_user.user_type == 'CUSTOMER':
        pass

    return render(request, 'success.html', context)
