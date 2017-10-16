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

    # check if bank user exist
    try:
        bank_user = models.BankUser.objects.get(user=user)
    except models.BankUser.DoesNotExist:
        context = {'msg': 'no BankUser found'}
        return render(request, 'error.html', context, status=400)

    if bank_user.state == 'INACTIVE':
        context = {'msg': 'not active BankUser'}
        return render(request, 'error.html', context, status=400)

    login(request, user)

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
    # POST method
    if request.method != "POST":
        context = {'msg': 'not post'}
        return render(request, 'error.html', context, status=400)

    # POST data
    f = form.AccountOpenForm(request.POST)
    if not f.is_valid():
        context = {'msg': 'not valid post data ' + str(f.errors)}
        return render(request, 'error.html', context, status=400)
    if request.POST['user_type'] not in ['CUSTOMER', 'MERCHANT']:
        context = {'msg': 'not valid user type'}
        return render(request, 'error.html', context, status=400)

    # get user
    try:
        _ = User.objects.get(username=request.POST['username'])
        context = {'msg': 'username exist'}
        return render(request, 'error.html', context, status=400)
    except User.DoesNotExist:
        pass

    # check phone
    try:
        _ = models.BankUser.objects.get(phone=request.POST['phone'])
        context = {'msg': 'phone exist'}
        return render(request, 'error.html', context, status=400)
    except models.BankUser.DoesNotExist:
        pass

    # check email
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
    bank_user = models.BankUser.objects.create(
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
        from_id=bank_user.id,
        to_id=bank_user.id,
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
    # valid user
    if not request.user.is_authenticated():
        context = {'msg': 'not authenticated'}
        return render(request, 'error.html', context, status=401)

    # bank user
    try:
        bank_user = models.BankUser.objects.get(user=request.user)
    except models.BankUser.DoesNotExist:
        context = {'msg': 'not authenticated'}
        return render(request, 'error.html', context, status=401)

    # GET data
    f = form.AccountUpdateGetForm(request.GET)
    if not f.is_valid():
        context = {'msg': 'not valid post data ' + str(f.errors)}
        return render(request, 'error.html', context, status=400)

    # update bank_user
    update_bank_user = models.BankUser.objects.get(id=request.GET['id'])

    context = {}
    if bank_user.user_type == 'ADMIN':
        context['username'] = update_bank_user.username
        context['id'] = update_bank_user.id
        context['phone'] = update_bank_user.phone
        context['email'] = update_bank_user.email
        context['address'] = update_bank_user.address
        return render(request, 'account_update.html', context)
    elif bank_user.user_type == 'TIER2':
        if update_bank_user.user_type in ['TIER2', 'TIER1', 'MERCHANT', 'CUSTOMER']:
            context['username'] = update_bank_user.username
            context['id'] = update_bank_user.id
            context['phone'] = update_bank_user.phone
            context['email'] = update_bank_user.email
            context['address'] = update_bank_user.address
            return render(request, 'account_update.html', context)
        else:
            context = {'msg': 'not authenticated'}
            return render(request, 'error.html', context, status=401)
    elif bank_user.user_type == 'TIER1':
        if update_bank_user.user_type in ['TIER1', 'MERCHANT', 'CUSTOMER']:
            context['username'] = update_bank_user.username
            context['id'] = update_bank_user.id
            context['phone'] = update_bank_user.phone
            context['email'] = update_bank_user.email
            context['address'] = update_bank_user.address
            return render(request, 'account_update.html', context)
        else:
            context = {'msg': 'not authenticated'}
            return render(request, 'error.html', context, status=401)
    elif bank_user.user_type == 'MERCHANT':
        if update_bank_user.id == bank_user.id:
            context['username'] = update_bank_user.username
            context['id'] = update_bank_user.id
            context['phone'] = update_bank_user.phone
            context['email'] = update_bank_user.email
            context['address'] = update_bank_user.address
            return render(request, 'account_update.html', context)
        else:
            context = {'msg': 'not authenticated'}
            return render(request, 'error.html', context, status=401)
    elif bank_user.user_type == 'CUSTOMER':
        if update_bank_user.id == bank_user.id:
            context['username'] = update_bank_user.username
            context['id'] = update_bank_user.id
            context['phone'] = update_bank_user.phone
            context['email'] = update_bank_user.email
            context['address'] = update_bank_user.address
            return render(request, 'account_update.html', context)
        else:
            context = {'msg': 'not authenticated'}
        return render(request, 'error.html', context, status=401)


def account_update_post_view(request):
    # valid user
    if not request.user.is_authenticated():
        context = {'msg': 'not authenticated'}
        return render(request, 'error.html', context, status=401)

    # bank user
    try:
        bank_user = models.BankUser.objects.get(user=request.user)
    except models.BankUser.DoesNotExist:
        context = {'msg': 'not authenticated'}
        return render(request, 'error.html', context, status=401)

    # POST data
    f = form.AccountUpdatePostForm(request.POST)
    if not f.is_valid():
        context = {'msg': 'not valid post data ' + str(f.errors)}
        return render(request, 'error.html', context, status=400)

    # update user
    try:
        update_bank_user = models.BankUser.objects.get(user=request.POST['id'])
    except models.BankUser.DoesNotExist:
        context = {'msg': 'updating user not exist'}
        return render(request, 'error.html', context, status=401)

    # check phone
    if update_bank_user.phone != request.POST['phone']:
        try:
            _ = models.BankUser.objects.get(phone=request.POST['phone'])
            context = {'msg': 'phone exist'}
            return render(request, 'error.html', context, status=400)
        except models.BankUser.DoesNotExist:
            pass

    # check email
    if update_bank_user.email != request.POST['email']:
        try:
            _ = models.BankUser.objects.get(email=request.POST['email'])
            context = {'msg': 'email exist'}
            return render(request, 'error.html', context, status=400)
        except models.BankUser.DoesNotExist:
            pass

    # permission
    if update_bank_user.user_type == 'ADMIN':
        permission = 3
    elif update_bank_user.user_type == 'TIER2':
        permission = 2
    elif update_bank_user.user_type == 'TIER1':
        permission = 1
    else:
        permission = 0

    # create Request
    models.Request.objects.create(
        from_id=bank_user.id,
        to_id=update_bank_user.id,
        created=datetime.datetime.now(),
        state='PENDING',
        request='ACCOUNT_UPDATE',
        permission=permission,
        phone=request.POST['phone'],
        email=request.POST['email'],
        address=request.POST['address'],
    )

    context = {'msg': 'Account Update Request sent'}
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
    RenderUser = collections.namedtuple('RenderUser', 'username user_type id email phone address')
    for u in users:
        context['users'].append(RenderUser(u.username, u.user_type, u.id, u.email, u.phone, u.address))

    # render request
    requests = models.Request.objects.all().exclude(user_type='ADMIN')
    RenderAccountOpenRequest = collections.namedtuple('RenderAccountOpenRequest',
                                                      'from_username to_username id state created request email phone address ')
    RenderAccountUpdateRequest = collections.namedtuple('RenderAccountUpdateRequest',
                                                      'from_username to_username id state created request email phone address ')

    for req in requests:
        # account open
        if req.request == 'ACCOUNT_OPEN':
            from_bank_user = models.BankUser.objects.get(id=req.from_id)
            to_bank_user = models.BankUser.objects.get(id=req.to_id)
            context['account_open_requests'].append(RenderAccountOpenRequest(
                from_bank_user.username, to_bank_user.username, req.id, req.state, req.created, req.request, req.email, req.phone, req.address
            ))
        # account update
        if req.request == 'ACCOUNT_UPDATE':
            from_bank_user = models.BankUser.objects.get(id=req.from_id)
            to_bank_user = models.BankUser.objects.get(id=req.to_id)
            context['account_update_requests'].append(RenderAccountUpdateRequest(
                from_bank_user.username, to_bank_user.username, req.id, req.state, req.created, req.request, req.email, req.phone, req.address
            ))
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
    f = form.HandleRequestForm(request.POST)
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
                # update bank_user
                update_bank_user = models.BankUser.objects.get(id=inner_request.to_id)
                update_bank_user.state = 'ACTIVE'
                update_bank_user.save()
                context['msg'] = 'APPROVED'
            else:
                inner_request.state = 'DECLINED'
                inner_request.save()
                context['msg'] = 'DECLINED'

        # ACCOUNT UPDATE
        elif inner_request.request == 'ACCOUNT_UPDATE':
            if int(request.POST['approve']):
                inner_request.state = 'APPROVED'
                inner_request.save()
                # update bank_user
                update_bank_user = models.BankUser.objects.get(id=inner_request.to_id)
                update_bank_user.phone = inner_request.phone
                update_bank_user.email = inner_request.email
                update_bank_user.address = inner_request.address
                update_bank_user.save()
                context['msg'] = 'APPROVED'
            else:
                inner_request.state = 'DECLINED'
                inner_request.save()
                context['msg'] = 'DECLINED'

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
