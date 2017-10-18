from django.shortcuts import render, redirect
import datetime
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from . import form
from . import models
import collections


RenderAccountOpenRequest = collections.namedtuple(
    'RenderAccountOpenRequest', 'from_username to_username id state created request email phone address')
RenderAccountUpdateRequest = collections.namedtuple(
    'RenderAccountUpdateRequest', 'from_username to_username id state created request email phone address')


# ----- login -----
def login_view(request):
    context = {}
    return render(request, 'login.html', context)


def login_post_view(request):
    # POST method
    if request.method != "POST":
        context = {'msg': 'not post'}
        return render(request, 'error.html', context, status=400)

    # POST data format
    f = form.LoginForm(request.POST)
    if not f.is_valid():
        context = {'msg': 'not valid post data'}
        return render(request, 'error.html', context, status=400)

    # login
    user = authenticate(username=request.POST['username'], password=request.POST['password'])
    if user is None:
        context = {'msg': 'not valid user or password'}
        return render(request, 'error.html', context, status=401)

    # active BankUser
    try:
        from_bank_user = models.BankUser.objects.get(user=user)
    except models.BankUser.DoesNotExist:
        context = {'msg': 'no BankUser found'}
        return render(request, 'error.html', context, status=400)

    if from_bank_user.state == 'INACTIVE':
        context = {'msg': 'not active BankUser'}
        return render(request, 'error.html', context, status=400)

    login(request, user)

    # redirect
    if from_bank_user.user_type == 'ADMIN':
        return redirect('/admin/')
    elif from_bank_user.user_type == 'TIER1':
        return redirect('/tier1/')
    elif from_bank_user.user_type == 'TIER2':
        return redirect('/tier2/')
    elif from_bank_user.user_type == 'CUSTOMER':
        return redirect('/customer/')
    elif from_bank_user.user_type == 'MERCHANT':
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

    # POST data format
    f = form.AccountOpenForm(request.POST)
    if not f.is_valid():
        context = {'msg': 'not valid post data ' + str(f.errors)}
        return render(request, 'error.html', context, status=400)
    if request.POST['user_type'] not in ['CUSTOMER', 'MERCHANT']:
        context = {'msg': 'not valid user type'}
        return render(request, 'error.html', context, status=400)

    # unique user
    try:
        _ = User.objects.get(username=request.POST['username'])
        context = {'msg': 'username exist'}
        return render(request, 'error.html', context, status=400)
    except User.DoesNotExist:
        pass

    # unique phone
    try:
        _ = models.BankUser.objects.get(phone=request.POST['phone'])
        context = {'msg': 'phone exist'}
        return render(request, 'error.html', context, status=400)
    except models.BankUser.DoesNotExist:
        pass

    # unique email
    try:
        _ = models.BankUser.objects.get(email=request.POST['email'])
        context = {'msg': 'email exist'}
        return render(request, 'error.html', context, status=400)
    except models.BankUser.DoesNotExist:
        pass

    # valid user
    if request.user.is_authenticated():

        # from bank user
        try:
            from_bankuser = models.BankUser.objects.get(user=request.user)
        except models.BankUser.DoesNotExist:
            context = {'msg': 'not authenticated'}
            return render(request, 'error.html', context, status=401)

        # ADMIN
        if from_bankuser.user_type == 'ADMIN':
            if request.POST['user_type'] not in ['TIER2', 'TIER1']:
                context = {'msg': 'admin only create tier2 tier1'}
                return render(request, 'error.html', context, status=401)
        # TIER2
        elif from_bankuser.user_type == 'TIER2':
            if request.POST['user_type'] not in ['CUSTOMER', 'MERCHANT']:
                context = {'msg': 'tier2 only create customer merchant'}
                return render(request, 'error.html', context, status=401)
        # TIER1
        elif from_bankuser.user_type == 'TIER1':
            if request.POST['user_type'] not in ['CUSTOMER', 'MERCHANT']:
                context = {'msg': 'tier1 only create customer merchant'}
                return render(request, 'error.html', context, status=401)
        else:
            context = {'msg': 'customer merchant cannot create user'}
            return render(request, 'error.html', context, status=401)
    else:
        from_bankuser = None
        if request.POST['user_type'] not in ['CUSTOMER', 'MERCHANT']:
            context = {'msg': 'unknown user only create customer merchant'}
            return render(request, 'error.html', context, status=401)

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
        from_id=from_bankuser.id if from_bankuser else bank_user.id,
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

    # from bank user
    try:
        from_bankuser = models.BankUser.objects.get(user=request.user)
    except models.BankUser.DoesNotExist:
        context = {'msg': 'from bank user not exist'}
        return render(request, 'error.html', context, status=401)

    # GET data format
    f = form.AccountUpdateGetForm(request.GET)
    if not f.is_valid():
        context = {'msg': 'not valid get data ' + str(f.errors)}
        return render(request, 'error.html', context, status=400)

    # to bank user
    try:
        to_bankuser = models.BankUser.objects.get(user=request.POST['id'])
    except models.BankUser.DoesNotExist:
        context = {'msg': 'to bank user not exist'}
        return render(request, 'error.html', context, status=401)

    # ADMIN
    if from_bankuser.user_type == 'ADMIN':
        if to_bankuser.user_type not in ['TIER2', 'TIER1']:
            context = {'msg': 'admin only update tier2 tier1'}
            return render(request, 'error.html', context, status=401)
    # TIER2
    elif from_bankuser.user_type == 'TIER2':
        if to_bankuser.user_type not in ['CUSTOMER', 'MERCHANT']:
            context = {'msg': 'tie2 only update customer merchant'}
            return render(request, 'error.html', context, status=401)
    # TIER1
    elif from_bankuser.user_type == 'TIER1':
        if to_bankuser.user_type not in ['CUSTOMER', 'MERCHANT']:
            context = {'msg': 'tie1 only update customer merchant'}
            return render(request, 'error.html', context, status=401)
    else:
        if from_bankuser.id != to_bankuser.id:
            context = {'msg': 'customer merchant only update self'}
            return render(request, 'error.html', context, status=401)

    context = {}
    context['username'] = to_bankuser.username
    context['id'] = to_bankuser.id
    context['phone'] = to_bankuser.phone
    context['email'] = to_bankuser.email
    context['address'] = to_bankuser.address
    return render(request, 'account_update.html', context)


def account_update_post_view(request):
    # valid user
    if not request.user.is_authenticated():
        context = {'msg': 'not authenticated'}
        return render(request, 'error.html', context, status=401)

    # from bank user
    try:
        from_bankuser = models.BankUser.objects.get(user=request.user)
    except models.BankUser.DoesNotExist:
        context = {'msg': 'from bank user not exist'}
        return render(request, 'error.html', context, status=401)

    # POST data format
    f = form.AccountUpdatePostForm(request.POST)
    if not f.is_valid():
        context = {'msg': 'not valid post data ' + str(f.errors)}
        return render(request, 'error.html', context, status=400)

    # to bank user
    try:
        to_bankuser = models.BankUser.objects.get(user=request.POST['id'])
    except models.BankUser.DoesNotExist:
        context = {'msg': 'to bank user not exist'}
        return render(request, 'error.html', context, status=401)

    # check phone
    if to_bankuser.phone != request.POST['phone']:
        try:
            _ = models.BankUser.objects.get(phone=request.POST['phone'])
            context = {'msg': 'phone exist'}
            return render(request, 'error.html', context, status=400)
        except models.BankUser.DoesNotExist:
            pass

    # check email
    if to_bankuser.email != request.POST['email']:
        try:
            _ = models.BankUser.objects.get(email=request.POST['email'])
            context = {'msg': 'email exist'}
            return render(request, 'error.html', context, status=400)
        except models.BankUser.DoesNotExist:
            pass

    # ADMIN
    if from_bankuser.user_type == 'ADMIN':
        if to_bankuser.user_type not in ['TIER2', 'TIER1']:
            context = {'msg': 'admin only update tier2 tier1'}
            return render(request, 'error.html', context, status=401)
    # TIER2
    elif from_bankuser.user_type == 'TIER2':
        if to_bankuser.user_type not in ['CUSTOMER', 'MERCHANT']:
            context = {'msg': 'tie2 only update customer merchant'}
            return render(request, 'error.html', context, status=401)
    # TIER1
    elif from_bankuser.user_type == 'TIER1':
        if to_bankuser.user_type not in ['CUSTOMER', 'MERCHANT']:
            context = {'msg': 'tie1 only update customer merchant'}
            return render(request, 'error.html', context, status=401)
    else:
        if from_bankuser.id != to_bankuser.id:
            context = {'msg': 'customer merchant only update self'}
            return render(request, 'error.html', context, status=401)

    # create Request
    models.Request.objects.create(
        from_id=from_bankuser.id,
        to_id=to_bankuser.id,
        user_type=to_bankuser.user_type,
        created=datetime.datetime.now(),
        state='PENDING',
        request='ACCOUNT_UPDATE',
        permission=0,
        phone=request.POST['phone'],
        email=request.POST['email'],
        address=request.POST['address'],
    )

    context = {'msg': 'Account Update Request sent'}
    return render(request, 'success.html', context)


# ----- 3. account delete -----
def account_delete_post_view(request):
    # valid user
    if not request.user.is_authenticated():
        context = {'msg': 'not authenticated'}
        return render(request, 'error.html', context, status=401)

    # from bank user
    try:
        from_bankuser = models.BankUser.objects.get(user=request.user)
    except models.BankUser.DoesNotExist:
        context = {'msg': 'from bank user not exist'}
        return render(request, 'error.html', context, status=401)

    # POST data format
    f = form.AccountDeleteGetForm(request.POST)
    if not f.is_valid():
        context = {'msg': 'not valid post data ' + str(f.errors)}
        return render(request, 'error.html', context, status=400)

    # to bank user
    try:
        to_bankuser = models.BankUser.objects.get(user=request.POST['id'])
    except models.BankUser.DoesNotExist:
        context = {'msg': 'to bank user not exist'}
        return render(request, 'error.html', context, status=401)

    # ADMIN
    if from_bankuser.user_type == 'ADMIN':
        if to_bankuser.user_type not in ['TIER2', 'TIER1']:
            context = {'msg': 'admin only delete tier2 tier1'}
            return render(request, 'error.html', context, status=401)
    # TIER2
    elif from_bankuser.user_type == 'TIER2':
        if to_bankuser.user_type not in ['CUSTOMER', 'MERCHANT']:
            context = {'msg': 'tie2 only delete customer merchant'}
            return render(request, 'error.html', context, status=401)
    # TIER1
    elif from_bankuser.user_type == 'TIER1':
        context = {'msg': 'tie1 cannot delete any account'}
        return render(request, 'error.html', context, status=401)
    else:
        context = {'msg': 'customer merchant cannot delete any account'}
        return render(request, 'error.html', context, status=401)

    to_user = to_bankuser.user
    to_bankuser.delete()
    to_user.delete()

    context = {'msg': 'Account deleted successfully'}
    return render(request, 'success.html', context)


# ------ 4. fund transfer -----
def make_transfer_view(request):
    context = {}
    return render(request, 'make_transfer.html', context)


def make_transfer_post_view(request):
    context = {}
    return render(request, 'success.html', context)


# ------ 5. payment -----
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
    users = models.BankUser.objects.all(
    ).exclude(user_type='ADMIN').exclude(
        user_type='CUSTOMER').exclude(
        user_type='MERCHANT')
    RenderUser = collections.namedtuple('RenderUser', 'username user_type id email phone address')
    for u in users:
        context['users'].append(RenderUser(u.username, u.user_type, u.id, u.email, u.phone, u.address))

    # render request
    inner_requests = models.Request.objects.all().exclude(user_type='ADMIN')

    for inner_request in inner_requests:
        from_bank_user = models.BankUser.objects.get(id=inner_request.from_id)
        to_bank_user = models.BankUser.objects.get(id=inner_request.to_id)

        # ACCOUNT OPEN for to bank user user_type tier2, tier1
        if inner_request.request == 'ACCOUNT_OPEN':
            if to_bank_user.user_type in ['TIER2', 'TIER1']:
                # from_username to_username id state created request email phone address
                context['account_open_requests'].append(RenderAccountUpdateRequest(
                    from_bank_user.username,
                    to_bank_user.username,
                    inner_request.id,
                    inner_request.state,
                    inner_request.created,
                    inner_request.request,
                    inner_request.email,
                    inner_request.phone,
                    inner_request.address
                ))

        # ACCOUNT UPDATE for to bank user user_type admin, tier2, tier1
        if inner_request.request == 'ACCOUNT_UPDATE':
            if to_bank_user.user_type in ['ADMIN', 'TIER2', 'TIER1']:
                # from_username to_username id state created request email phone address
                context['account_update_requests'].append(RenderAccountUpdateRequest(
                    from_bank_user.username,
                    to_bank_user.username,
                    inner_request.id,
                    inner_request.state,
                    inner_request.created,
                    inner_request.request,
                    inner_request.email,
                    inner_request.phone,
                    inner_request.address
                ))
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
def request_approve_post_view(request):

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

    # get user
    from_bankuser = models.BankUser.objects.get(id=inner_request.from_id)
    to_bankuser = models.BankUser.objects.get(id=inner_request.to_id)

    # ADMIN
    if bank_user.user_type == 'ADMIN':
        # ACCOUNT OPEN
        if inner_request.request == 'ACCOUNT_OPEN':
            if to_bankuser.user_type in ['TIER2', 'TIER1']:
                if int(request.POST['approve']):
                    inner_request.state = 'APPROVED'
                    inner_request.save()
                    # update bank_user
                    to_bankuser.state = 'ACTIVE'
                    to_bankuser.save()
                    context['msg'] = 'APPROVED'
                    return render(request, 'success.html', context)
                else:
                    inner_request.state = 'DECLINED'
                    inner_request.save()
                    context['msg'] = 'admin can only open tier2, tier1'
            else:
                return render(request, 'error.html', context, status=401)

        # ACCOUNT UPDATE
        elif inner_request.request == 'ACCOUNT_UPDATE' and to_bankuser.user_type in ['ADMIN', 'TIER2', 'TIER1']:
            if int(request.POST['approve']):
                inner_request.state = 'APPROVED'
                inner_request.save()
                # update bank_user
                to_bankuser.phone = inner_request.phone
                to_bankuser.email = inner_request.email
                to_bankuser.address = inner_request.address
                to_bankuser.save()
                context['msg'] = 'APPROVED'
                return render(request, 'success.html', context)
            else:
                inner_request.state = 'DECLINED'
                inner_request.save()
                context['msg'] = 'admin can update open admin, tier2, tier1'
                context['msg'] = 'DECLINED'
                return render(request, 'error.html', context, status=401)

        # ACCOUNT DELETE
        elif inner_request.request == 'ACCOUNT_DELETE' and to_bankuser.user_type in ['TIER2', 'TIER2']:
            if int(request.POST['approve']):
                inner_request.state = 'APPROVED'
                inner_request.save()
                # delete bank_user
                to_user = to_bankuser.user
                to_bankuser.delete()
                to_user.delete()
                context['msg'] = 'APPROVED'
            else:
                inner_request.state = 'DECLINED'
                inner_request.save()
                context['msg'] = 'DECLINED'
        else:
            context['msg'] = 'admin can only approve or decline internal account open/update/delete'
            return render(request, 'error.html', context, status=401)
    elif bank_user.user_type == 'TIER1':
        pass
    elif bank_user.user_type == 'TIER2':
        pass
    elif bank_user.user_type == 'MERCHANT':
        pass
    elif bank_user.user_type == 'CUSTOMER':
        pass

    context['msg'] = 'DECLINED'
    return render(request, 'error.html', context, status=401)
