from django.shortcuts import render, redirect
import datetime
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from . import form
from . import models
import collections
from django.db.models import Q


RenderUser = collections.namedtuple(
    'RenderUser', 'username user_type state id email phone address')
RenderAccountOpenRequest = collections.namedtuple(
    'RenderAccountOpenRequest', 'from_username to_username id state sub_state created request email phone address')
RenderAccountUpdateRequest = collections.namedtuple(
    'RenderAccountUpdateRequest', 'from_username to_username id state sub_state created request email phone address')
RenderApproveRequest = collections.namedtuple(
    'RenderApproveRequest', 'from_username to_username id state sub_state target_state created request email phone address')


# ----- login -----
def login_view(request):

    # valid user
    if request.user.is_authenticated():
        # from bank user
        try:
            login_bankuser = models.BankUser.objects.get(user=request.user)
        except models.BankUser.DoesNotExist:
            context = {'msg': 'from bank user not exist'}
            return render(request, 'error.html', context, status=401)

        # active bank user
        if login_bankuser.state == 'INACTIVE':
            context = {'msg': 'not active BankUser'}
            return render(request, 'error.html', context, status=400)

        # redirect
        if login_bankuser.user_type == 'ADMIN':
            return redirect('/admin/')
        elif login_bankuser.user_type == 'TIER1':
            return redirect('/tier1/')
        elif login_bankuser.user_type == 'TIER2':
            return redirect('/tier2/')
        elif login_bankuser.user_type == 'CUSTOMER':
            return redirect('/customer/')
        elif login_bankuser.user_type == 'MERCHANT':
            return redirect('/merchant/')
        else:
            return redirect('/logout/')
    else:
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
        context = {'msg': 'not valid post data', 'form': f}
        return render(request, 'error.html', context, status=400)

    # login
    user = authenticate(username=request.POST['username'], password=request.POST['password'])
    if user is None:
        context = {'msg': 'not valid user or password'}
        return render(request, 'error.html', context, status=401)

    # active BankUser
    try:
        login_bankuser = models.BankUser.objects.get(user=user)
    except models.BankUser.DoesNotExist:
        context = {'msg': 'no BankUser found'}
        return render(request, 'error.html', context, status=400)

    if login_bankuser.state == 'INACTIVE':
        context = {'msg': 'not active BankUser'}
        return render(request, 'error.html', context, status=400)

    login(request, user)

    # redirect
    if login_bankuser.user_type == 'ADMIN':
        return redirect('/admin/')
    elif login_bankuser.user_type == 'TIER1':
        return redirect('/tier1/')
    elif login_bankuser.user_type == 'TIER2':
        return redirect('/tier2/')
    elif login_bankuser.user_type == 'CUSTOMER':
        return redirect('/customer/')
    elif login_bankuser.user_type == 'MERCHANT':
        return redirect('/merchant/')
    else:
        return redirect('/logout/')


def logout_view(request):
    context = {}
    logout(request)
    return render(request, 'logout.html', context)


# ------ 1. account open -----
def account_open_view(request):

    # valid user
    if request.user.is_authenticated():
        # active BankUser
        try:
            login_bankuser = models.BankUser.objects.get(user=request.user)
        except models.BankUser.DoesNotExist:
            context = {'msg': 'no BankUser found'}
            return render(request, 'error.html', context, status=400)
        if login_bankuser.state == 'INACTIVE':
            context = {'msg': 'not active BankUser'}
            return render(request, 'error.html', context, status=400)

        context = {'user_type': login_bankuser.user_type}
        return render(request, 'account_open.html', context)
    else:
        context = {'user_type': ''}
        return render(request, 'account_open.html', context)


def account_open_post_view(request):

    # POST method
    if request.method != "POST":
        context = {'msg': 'not post'}
        return render(request, 'error.html', context, status=400)

    # POST data format
    f = form.AccountOpenForm(request.POST)
    if not f.is_valid():
        context = {'msg': 'not valid post data ', 'form': f}
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

        # active bank user
        if from_bankuser.state == 'INACTIVE':
            context = {'msg': 'not active BankUser'}
            return render(request, 'error.html', context, status=400)

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
        sub_state='WAITING_T2',
        request='ACCOUNT_OPEN',
        permission=0,
        user_type=request.POST['user_type'],
        critical=0,
        request_id=-1,
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

    # active bank user
    if from_bankuser.state == 'INACTIVE':
        context = {'msg': 'not active BankUser'}
        return render(request, 'error.html', context, status=400)

    # GET data format
    f = form.AccountUpdateGetForm(request.GET)
    if not f.is_valid():
        context = {'msg': 'not valid get data ', 'form': f}
        return render(request, 'error.html', context, status=400)

    # to bank user
    try:
        to_bankuser = models.BankUser.objects.get(user=request.GET['id'])
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
        if to_bankuser.user_type in ['CUSTOMER', 'MERCHANT']:
            pass
        elif to_bankuser.id == from_bankuser.id:
            pass
        else:
            context = {'msg': 'tier1 only update self, customer, merchant'}
            return render(request, 'error.html', context, status=401)
    # TIER1
    elif from_bankuser.user_type == 'TIER1':
        if to_bankuser.user_type in ['CUSTOMER', 'MERCHANT']:
            pass
        elif to_bankuser.id == from_bankuser.id:
            pass
        else:
            context = {'msg': 'tier1 only update self, customer, merchant'}
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

    # active bank user
    if from_bankuser.state == 'INACTIVE':
        context = {'msg': 'not active BankUser'}
        return render(request, 'error.html', context, status=400)

    # POST data format
    f = form.AccountUpdatePostForm(request.POST)
    if not f.is_valid():
        context = {'msg': 'not valid post data ', 'form': f}
        return render(request, 'error.html', context, status=400)

    # to bank user
    try:
        to_bankuser = models.BankUser.objects.get(user=request.POST['id'])
    except models.BankUser.DoesNotExist:
        context = {'msg': 'to bank user not exist'}
        return render(request, 'error.html', context, status=401)

    # check phone
    if request.POST.get('phone', '').strip():
        if request.POST['phone'].strip() != to_bankuser.phone:
            try:
                _ = models.BankUser.objects.get(phone=request.POST['phone'].strip())
                context = {'msg': 'phone exist'}
                return render(request, 'error.html', context, status=400)
            except models.BankUser.DoesNotExist:
                pass

    # check email
    if request.POST.get('email', '').strip():
        if request.POST['email'].strip() != to_bankuser.email:
            try:
                _ = models.BankUser.objects.get(email=request.POST['email'].strip())
                context = {'msg': 'email exist'}
                return render(request, 'error.html', context, status=400)
            except models.BankUser.DoesNotExist:
                pass

    # sub-state for T1, 'WAITING_T2', 'WAITING_T2_EX', 'WAITING_EX', 'WAITING'
    sub_state = 'WAITING_T2_EX'

    # ADMIN
    if from_bankuser.user_type == 'ADMIN':
        if to_bankuser.user_type not in ['TIER2', 'TIER1']:
            context = {'msg': 'admin only update tier2 tier1'}
            return render(request, 'error.html', context, status=401)
    # TIER2
    elif from_bankuser.user_type == 'TIER2':
        if to_bankuser.user_type in ['CUSTOMER', 'MERCHANT']:
            pass
        elif to_bankuser.id == from_bankuser.id:
            pass
        else:
            context = {'msg': 'tier1 only update self, customer, merchant'}
            return render(request, 'error.html', context, status=401)
    # TIER1
    elif from_bankuser.user_type == 'TIER1':
        if to_bankuser.user_type in ['CUSTOMER', 'MERCHANT']:
            pass
        elif to_bankuser.id == from_bankuser.id:
            pass
        else:
            context = {'msg': 'tier1 only update self, customer, merchant'}
            return render(request, 'error.html', context, status=401)
    else:
        if from_bankuser.id != to_bankuser.id:
            context = {'msg': 'customer merchant only update self'}
            return render(request, 'error.html', context, status=401)
        sub_state = 'WAITING_T2'

    # create Request
    models.Request.objects.create(
        from_id=from_bankuser.id,
        to_id=to_bankuser.id,
        user_type=to_bankuser.user_type,
        created=datetime.datetime.now(),
        state='PENDING',
        sub_state=sub_state,
        request='ACCOUNT_UPDATE',
        permission=0,
        critical=0,
        request_id=-1,
        phone=request.POST.get('phone', '').strip(),
        email=request.POST.get('email', '').strip(),
        address=request.POST.get('address', '').strip(),
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

    # active bank user
    if from_bankuser.state == 'INACTIVE':
        context = {'msg': 'not active BankUser'}
        return render(request, 'error.html', context, status=400)

    # POST data format
    f = form.AccountDeleteGetForm(request.POST)
    if not f.is_valid():
        context = {'msg': 'not valid post data ', 'form': f}
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

    # delete bank_user
    to_bankuser.state = 'INACTIVE'
    to_bankuser.save()

    # decline related pending requests
    to_bankuser_reqs = models.Request.objects.filter(Q(from_id=to_bankuser.id) | Q(to_id=to_bankuser.id))
    for req in to_bankuser_reqs:
        if req.state == 'PENDING':
            req.state = 'DECLINED'
            req.save()

    context = {'msg': 'Account deleted successfully'}
    return render(request, 'success.html', context)


# ------ 4. fund transfer -----
def make_transfer_view(request):
    # valid user
    if not request.user.is_authenticated():
        context = {'msg': 'not authenticated'}
        return render(request, 'error.html', context, status=401)

    # login bank user
    try:
        login_bankuser = models.BankUser.objects.get(user=request.user)
    except models.BankUser.DoesNotExist:
        context = {'msg': 'from bank user not exist'}
        return render(request, 'error.html', context, status=401)

    # active bank user
    if login_bankuser.state == 'INACTIVE':
        context = {'msg': 'not active BankUser'}
        return render(request, 'error.html', context, status=400)

    # render user
    context = {}
    user = RenderUser(
        login_bankuser.username,
        login_bankuser.user_type,
        login_bankuser.state,
        login_bankuser.id,
        login_bankuser.email,
        login_bankuser.phone,
        login_bankuser.address
    )
    context['user'] = user

    return render(request, 'make_transfer.html', context)


def make_transfer_post_view(request):

    # valid user
    if not request.user.is_authenticated():
        context = {'msg': 'not authenticated'}
        return render(request, 'error.html', context, status=401)

    # login bank user
    try:
        login_bankuser = models.BankUser.objects.get(user=request.user)
    except models.BankUser.DoesNotExist:
        context = {'msg': 'from bank user not exist'}
        return render(request, 'error.html', context, status=401)

    # active bank user
    if login_bankuser.state == 'INACTIVE':
        context = {'msg': 'not active BankUser'}
        return render(request, 'error.html', context, status=400)

    # POST data format
    f = form.MakeTransferPostForm(request.POST)
    if not f.is_valid():
        context = {'msg': 'not valid post data ', 'form': f}
        return render(request, 'error.html', context, status=400)

    # balance type
    if request.POST['from_balance'] not in ['CREDIT', 'CHECKING', 'SAVING']:
        context = {'msg': 'not valid from_balance'}
        return render(request, 'error.html', context, status=400)
    if request.POST['to_balance'] not in ['CREDIT', 'CHECKING', 'SAVING']:
        context = {'msg': 'not valid from_balance'}
        return render(request, 'error.html', context, status=400)

    sub_state = 'WAITING_T2_EX'
    if login_bankuser.user_type == 'ADMIN':
        context = {'msg': 'admin can not transfer money'}
        return render(request, 'error.html', context, status=400)
    elif login_bankuser.user_type == 'TIER2':
        context = {'msg': 't2 can not transfer money'}
        return render(request, 'error.html', context, status=400)
    elif login_bankuser.user_type == 'TIER1':
        context = {'msg': 't1 can not transfer money'}
        return render(request, 'error.html', context, status=400)
    elif login_bankuser.user_type == 'CUSTOMER':
        sub_state = 'WAITING_T2'
    elif login_bankuser.user_type == 'MERCHANT':
        sub_state = 'WAITING_T2'
    else:
        context = {'msg': 'unknown user'}
        return render(request, 'error.html', context, status=400)

    from_bankuser = login_bankuser
    try:
        to_bankuser = models.BankUser.objects.get(email=request.POST['to_email'])
    except models.BankUser.DoesNotExist:
        context = {'msg': 'to bank user not exist'}
        return render(request, 'error.html', context, status=401)

    # check transfer logical
    if from_bankuser == to_bankuser:
        pass
    else:
        if request.POST['from_balance'] != 'CHECKING' or request.POST['to_balance'] != 'CHECKING':
            context = {'msg': 'different user only allow transfer between checking'}
            return render(request, 'error.html', context, status=400)

    # create Request
    models.Request.objects.create(
        from_id=from_bankuser.id,
        to_id=to_bankuser.id if to_bankuser else -1,
        user_type='CUSTOMER',
        created=datetime.datetime.now(),
        state='PENDING',
        # sub-state for T1, 'WAITING_T2', 'WAITING_T2_EX', 'WAITING_EX', 'WAITING'
        sub_state=sub_state,
        request='FUND',
        request_id=-1,
        permission=-1,
        critical=1 if int(request.POST['money']) > 1000 else 0,
        money=request.POST['money'],
        phone=request.POST.get('phone', '').strip(),
        email=request.POST.get('email', '').strip(),
        address=request.POST.get('address', '').strip(),
    )

    context = {'msg': 'TRANSFER REQUEST sent'}
    return render(request, 'success.html', context)


# ------ 5. payment -----
def make_payment_view(request):
    context = {}
    return render(request, 'make_payment.html', context)


def make_payment_post_view(request):
    context = {}
    return render(request, 'success.html', context)


# ------ 6. debit/credit -----
def make_debit_view(request):
    context = {}
    return render(request, 'make_payment.html', context)


def make_debit_post_view(request):
    context = {}
    return render(request, 'success.html', context)


# ------ 7. request -----
def make_approve_request_post_view(request):

    # bank user
    try:
        login_bankuser = models.BankUser.objects.get(user=request.user)
    except models.BankUser.DoesNotExist:
        context = {'msg': 'not authenticated'}
        return render(request, 'error.html', context, status=401)

    # active bank user
    if login_bankuser.state == 'INACTIVE':
        context = {'msg': 'not active BankUser'}
        return render(request, 'error.html', context, status=400)

    # t1
    if login_bankuser.user_type != 'TIER1':
        context = {'msg': 'only t1 can send APPROVE REQUEST'}
        return render(request, 'error.html', context, status=400)

    # POST data format
    f = form.ApproveRequestForm(request.POST)
    if not f.is_valid():
        context = {'msg': 'not valid post data ', 'form': f}
        return render(request, 'error.html', context, status=400)

    # from bank user
    from_bankuser = login_bankuser

    # user_type is customer or tier2
    if request.POST['user_type'] == 'CUSTOMER':
        try:
            to_bankuser = models.BankUser.objects.get(username=request.POST['to_username'])
        except models.BankUser.DoesNotExist:
            context = {'msg': 'to bank user not exist'}
            return render(request, 'error.html', context, status=401)
    else:
        to_bankuser = None

    # to request id
    try:
        inner_request = models.Request.objects.get(id=request.POST['request_id'])
    except models.Request.DoesNotExist:
        context = {'msg': 'request not exist'}
        return render(request, 'error.html', context, status=401)

    # create Request
    models.Request.objects.create(
        from_id=from_bankuser.id,
        to_id=to_bankuser.id if to_bankuser else -1,
        user_type=request.POST['user_type'],
        created=datetime.datetime.now(),
        state='PENDING',
        # sub-state for T1, 'WAITING_T2', 'WAITING_T2_EX', 'WAITING_EX', 'WAITING'
        sub_state='WAITING',
        request='APPROVE_REQUEST',
        request_id=inner_request.id,
        permission=0,
        critical=0,
        phone=request.POST.get('phone', '').strip(),
        email=request.POST.get('email', '').strip(),
        address=request.POST.get('address', '').strip(),
    )

    context = {'msg': 'APPROVE REQUEST sent'}
    return render(request, 'success.html', context)


# ----- index -----
def index_view(request):
    if not request.user.is_authenticated():
        return redirect('/login/')

    # check if it is an admin user
    try:
        from_bankuser = models.BankUser.objects.get(user=request.user)
    except models.BankUser.DoesNotExist:
        context = {'msg': 'not authenticated'}
        return render(request, 'error.html', context, status=401)

    # active bank user
    if from_bankuser.state == 'INACTIVE':
        context = {'msg': 'not active BankUser'}
        return render(request, 'error.html', context, status=400)

    # redirect
    if from_bankuser.user_type == 'ADMIN':
        return redirect('/admin/')
    elif from_bankuser.user_type == 'TIER1':
        return redirect('/tier1/')
    elif from_bankuser.user_type == 'TIER2':
        return redirect('/tier2/')
    elif from_bankuser.user_type == 'CUSTOMER':
        return redirect('/customer/')
    elif from_bankuser.user_type == 'MERCHANT':
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
        login_bankuser = models.BankUser.objects.get(user=request.user)
    except models.BankUser.DoesNotExist:
        context = {'msg': 'not authenticated'}
        return render(request, 'error.html', context, status=401)
    if login_bankuser.user_type != 'ADMIN':
        context = {'msg': 'not authenticated'}
        return render(request, 'error.html', context, status=401)

    # active bank user
    if login_bankuser.state == 'INACTIVE':
        context = {'msg': 'not active BankUser'}
        return render(request, 'error.html', context, status=400)

    context = {
        'user': None,
        'users': [],
        'account_open_requests': [],
        'account_update_requests': [],
        'fund_requests': [],
        'payment_requests': [],
    }

    # render user
    user = RenderUser(
        login_bankuser.username,
        login_bankuser.user_type,
        login_bankuser.state,
        login_bankuser.id,
        login_bankuser.email,
        login_bankuser.phone,
        login_bankuser.address
    )
    context['user'] = user

    # render users
    users = models.BankUser.objects.all(
    ).exclude(user_type='ADMIN').exclude(
        user_type='CUSTOMER').exclude(
        user_type='MERCHANT')
    for u in users:
        context['users'].append(RenderUser(u.username, u.user_type, u.state, u.id, u.email, u.phone, u.address))

    # render request
    inner_requests = models.Request.objects.all()

    for inner_request in inner_requests:
        try:
            from_bank_user = models.BankUser.objects.get(id=inner_request.from_id)
        except models.BankUser.DoesNotExist:
            from_bank_user = None
        try:
            to_bank_user = models.BankUser.objects.get(id=inner_request.to_id)
        except models.BankUser.DoesNotExist:
            to_bank_user = None

        # ACCOUNT OPEN for to bank user user_type tier2, tier1
        if inner_request.request == 'ACCOUNT_OPEN':
            if to_bank_user.user_type in ['TIER2', 'TIER1']:
                # from_username to_username id state created request email phone address
                context['account_open_requests'].append(RenderAccountOpenRequest(
                    from_bank_user.username if from_bank_user else 'obsolete user',
                    to_bank_user.username if to_bank_user else 'obsolete user',
                    inner_request.id,
                    inner_request.state,
                    inner_request.sub_state,
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
                    from_bank_user.username if from_bank_user else 'obsolete user',
                    to_bank_user.username if to_bank_user else 'obsolete user',
                    inner_request.id,
                    inner_request.state,
                    inner_request.sub_state,
                    inner_request.created,
                    inner_request.request,
                    inner_request.email,
                    inner_request.phone,
                    inner_request.address
                ))

    # return HttpResponse(str(context))
    return render(request, 'admin.html', context)


# ----- tier2 -----
def tier2_view(request):

    # check if a valid user
    if not request.user.is_authenticated():
        context = {'msg': 'not authenticated'}
        return render(request, 'error.html', context, status=401)

    # check if it is an admin user
    try:
        login_bankuser = models.BankUser.objects.get(user=request.user)
    except models.BankUser.DoesNotExist:
        context = {'msg': 'not authenticated'}
        return render(request, 'error.html', context, status=401)
    if login_bankuser.user_type != 'TIER2':
        context = {'msg': 'not authenticated'}
        return render(request, 'error.html', context, status=401)

    # active bank user
    if login_bankuser.state == 'INACTIVE':
        context = {'msg': 'not active BankUser'}
        return render(request, 'error.html', context, status=400)

    context = {
        'user': None,
        'users': [],
        'account_open_requests': [],
        'account_update_requests': [],
        'approve_requests': [],
        'fund_requests': [],
        'payment_requests': [],
    }

    # render user
    user = RenderUser(
        login_bankuser.username,
        login_bankuser.user_type,
        login_bankuser.state,
        login_bankuser.id,
        login_bankuser.email,
        login_bankuser.phone,
        login_bankuser.address
    )
    context['user'] = user

    # render users
    users = models.BankUser.objects.all(
    ).exclude(user_type='ADMIN').exclude(
        user_type='TIER2').exclude(
        user_type='TIER1')
    for u in users:
        context['users'].append(RenderUser(u.username, u.user_type, u.state, u.id, '***', '***', '***'))

    # render request
    inner_requests = models.Request.objects.all()

    for inner_request in inner_requests:
        try:
            from_bank_user = models.BankUser.objects.get(id=inner_request.from_id)
        except models.BankUser.DoesNotExist:
            from_bank_user = None
        try:
            to_bank_user = models.BankUser.objects.get(id=inner_request.to_id)
        except models.BankUser.DoesNotExist:
            to_bank_user = None

        # ACCOUNT OPEN
        if inner_request.request == 'ACCOUNT_OPEN':
            if to_bank_user.user_type in ['CUSTOMER', 'MERCHANT']:
                context['account_open_requests'].append(RenderAccountOpenRequest(
                    from_bank_user.username if from_bank_user else 'obsolete user',
                    to_bank_user.username if to_bank_user else 'obsolete user',
                    inner_request.id,
                    inner_request.state,
                    inner_request.sub_state,
                    inner_request.created,
                    inner_request.request,
                    inner_request.email,
                    inner_request.phone,
                    inner_request.address
                ))

        # ACCOUNT UPDATE
        if inner_request.request == 'ACCOUNT_UPDATE':
            if to_bank_user.user_type in ['CUSTOMER', 'MERCHANT']:
                context['account_update_requests'].append(RenderAccountUpdateRequest(
                    from_bank_user.username if from_bank_user else 'obsolete user',
                    to_bank_user.username if to_bank_user else 'obsolete user',
                    inner_request.id,
                    inner_request.state,
                    inner_request.sub_state,
                    inner_request.created,
                    inner_request.request,
                    inner_request.email,
                    inner_request.phone,
                    inner_request.address
                ))

        # APPROVE REQUEST
        if inner_request.request == 'APPROVE_REQUEST':
            if inner_request.user_type == 'TIER2':
                try:
                    target_inner_request = models.Request.objects.get(id=inner_request.request_id)
                except models.Request.DoesNotExist:
                    context = {'msg': 'not valid request '}
                    return render(request, 'error.html', context, status=401)
                context['approve_requests'].append(RenderApproveRequest(
                    from_bank_user.username if from_bank_user else 'obsolete user',
                    to_bank_user.username if to_bank_user else 'obsolete user',
                    inner_request.id,
                    inner_request.state,
                    inner_request.sub_state,
                    target_inner_request.request,
                    inner_request.created,
                    inner_request.request,
                    inner_request.email,
                    inner_request.phone,
                    inner_request.address
                ))

    return render(request, 'tier2.html', context)


# ----- tier1 -----
def tier1_view(request):

    # check if a valid user
    if not request.user.is_authenticated():
        context = {'msg': 'not authenticated'}
        return render(request, 'error.html', context, status=401)

    # check if it is an admin user
    try:
        login_bankuser = models.BankUser.objects.get(user=request.user)
    except models.BankUser.DoesNotExist:
        context = {'msg': 'not authenticated'}
        return render(request, 'error.html', context, status=401)
    if login_bankuser.user_type != 'TIER1':
        context = {'msg': 'not authenticated'}
        return render(request, 'error.html', context, status=401)

    # active bank user
    if login_bankuser.state == 'INACTIVE':
        context = {'msg': 'not active BankUser'}
        return render(request, 'error.html', context, status=400)

    context = {
        'user': None,
        'users': [],
        'account_open_requests': [],
        'account_update_requests': [],
        'fund_requests': [],
        'payment_requests': [],
    }

    # render user
    user = RenderUser(
        login_bankuser.username,
        login_bankuser.user_type,
        login_bankuser.state,
        login_bankuser.id,
        login_bankuser.email,
        login_bankuser.phone,
        login_bankuser.address
    )
    context['user'] = user

    # render users
    users = models.BankUser.objects.all(
    ).exclude(user_type='ADMIN').exclude(
        user_type='TIER2').exclude(
        user_type='TIER1')
    for u in users:
        context['users'].append(RenderUser(u.username, u.user_type, u.state, u.id, '***', '***', '***'))

    # render request
    inner_requests = models.Request.objects.all()

    for inner_request in inner_requests:
        try:
            from_bank_user = models.BankUser.objects.get(id=inner_request.from_id)
        except models.BankUser.DoesNotExist:
            from_bank_user = None
        try:
            to_bank_user = models.BankUser.objects.get(id=inner_request.to_id)
        except models.BankUser.DoesNotExist:
            to_bank_user = None

        # ACCOUNT OPEN
        if inner_request.request == 'ACCOUNT_OPEN':
            if to_bank_user.user_type in ['CUSTOMER', 'MERCHANT']:
                context['account_open_requests'].append(RenderAccountOpenRequest(
                    from_bank_user.username if from_bank_user else 'obsolete user',
                    to_bank_user.username if to_bank_user else 'obsolete user',
                    inner_request.id,
                    inner_request.state,
                    inner_request.sub_state,
                    inner_request.created,
                    inner_request.request,
                    inner_request.email,
                    inner_request.phone,
                    inner_request.address
                ))

        # ACCOUNT UPDATE
        if inner_request.request == 'ACCOUNT_UPDATE':
            if to_bank_user.user_type in ['CUSTOMER', 'MERCHANT']:
                context['account_update_requests'].append(RenderAccountUpdateRequest(
                    from_bank_user.username if from_bank_user else 'obsolete user',
                    to_bank_user.username if to_bank_user else 'obsolete user',
                    inner_request.id,
                    inner_request.state,
                    inner_request.sub_state,
                    inner_request.created,
                    inner_request.request,
                    inner_request.email,
                    inner_request.phone,
                    inner_request.address
                ))

    return render(request, 'tier1.html', context)


# ----- customer -----
def customer_view(request):

    # check if a valid user
    if not request.user.is_authenticated():
        context = {'msg': 'not authenticated'}
        return render(request, 'error.html', context, status=401)

    # check if it is an admin user
    try:
        login_bankuser = models.BankUser.objects.get(user=request.user)
    except models.BankUser.DoesNotExist:
        context = {'msg': 'not authenticated'}
        return render(request, 'error.html', context, status=401)
    if login_bankuser.user_type != 'CUSTOMER':
        context = {'msg': 'not authenticated'}
        return render(request, 'error.html', context, status=401)

    # active bank user
    if login_bankuser.state == 'INACTIVE':
        context = {'msg': 'not active BankUser'}
        return render(request, 'error.html', context, status=400)

    context = {
        'user': None,
        'users': [],
        'account_open_requests': [],
        'account_update_requests': [],
        'approve_requests': [],
        'fund_requests': [],
        'payment_requests': [],
    }

    # render user
    user = RenderUser(
        login_bankuser.username,
        login_bankuser.user_type,
        login_bankuser.state,
        login_bankuser.id,
        login_bankuser.email,
        login_bankuser.phone,
        login_bankuser.address
    )
    context['user'] = user

    # render request
    inner_requests = models.Request.objects.all()

    for inner_request in inner_requests:
        try:
            from_bank_user = models.BankUser.objects.get(id=inner_request.from_id)
        except models.BankUser.DoesNotExist:
            from_bank_user = None
        try:
            to_bank_user = models.BankUser.objects.get(id=inner_request.to_id)
        except models.BankUser.DoesNotExist:
            to_bank_user = None

        # APPROVE REQUEST
        if inner_request.request == 'APPROVE_REQUEST':
            if inner_request.to_id == login_bankuser.id:
                try:
                    target_inner_request = models.Request.objects.get(id=inner_request.request_id)
                except models.Request.DoesNotExist:
                    context = {'msg': 'not valid request '}
                    return render(request, 'error.html', context, status=401)
                context['approve_requests'].append(RenderApproveRequest(
                    from_bank_user.username if from_bank_user else 'obsolete user',
                    to_bank_user.username if to_bank_user else 'obsolete user',
                    inner_request.id,
                    inner_request.state,
                    inner_request.sub_state,
                    target_inner_request.request,
                    inner_request.created,
                    inner_request.request,
                    inner_request.email,
                    inner_request.phone,
                    inner_request.address
                ))

    return render(request, 'customer.html', context)


# ----- merchant -----
def merchant_view(request):
    # check if a valid user
    if not request.user.is_authenticated():
        context = {'msg': 'not authenticated'}
        return render(request, 'error.html', context, status=401)

    # check if it is an admin user
    try:
        login_bankuser = models.BankUser.objects.get(user=request.user)
    except models.BankUser.DoesNotExist:
        context = {'msg': 'not authenticated'}
        return render(request, 'error.html', context, status=401)
    if login_bankuser.user_type != 'MERCHANT':
        context = {'msg': 'not authenticated'}
        return render(request, 'error.html', context, status=401)

    # active bank user
    if login_bankuser.state == 'INACTIVE':
        context = {'msg': 'not active BankUser'}
        return render(request, 'error.html', context, status=400)

    context = {
        'user': None,
        'users': [],
        'account_open_requests': [],
        'account_update_requests': [],
        'approve_requests': [],
        'fund_requests': [],
        'payment_requests': [],
    }

    # render user
    user = RenderUser(
        login_bankuser.username,
        login_bankuser.user_type,
        login_bankuser.state,
        login_bankuser.id,
        login_bankuser.email,
        login_bankuser.phone,
        login_bankuser.address
    )
    context['user'] = user

    # render request
    inner_requests = models.Request.objects.all()

    for inner_request in inner_requests:
        try:
            from_bank_user = models.BankUser.objects.get(id=inner_request.from_id)
        except models.BankUser.DoesNotExist:
            from_bank_user = None
        try:
            to_bank_user = models.BankUser.objects.get(id=inner_request.to_id)
        except models.BankUser.DoesNotExist:
            to_bank_user = None

        # APPROVE REQUEST
        if inner_request.request == 'APPROVE_REQUEST':
            if inner_request.to_id == login_bankuser.id:
                try:
                    target_inner_request = models.Request.objects.get(id=inner_request.request_id)
                except models.Request.DoesNotExist:
                    context = {'msg': 'not valid request '}
                    return render(request, 'error.html', context, status=401)
                context['approve_requests'].append(RenderApproveRequest(
                    from_bank_user.username if from_bank_user else 'obsolete user',
                    to_bank_user.username if to_bank_user else 'obsolete user',
                    inner_request.id,
                    inner_request.state,
                    inner_request.sub_state,
                    target_inner_request.request,
                    inner_request.created,
                    inner_request.request,
                    inner_request.email,
                    inner_request.phone,
                    inner_request.address
                ))

    return render(request, 'merchant.html', context)


# ----- request ----
def request_approve_post_view(request):

    context = {}

    # check if a valid user
    if not request.user.is_authenticated():
        context = {'msg': 'not authenticated'}
        return render(request, 'error.html', context, status=401)
    try:
        login_bankuser = models.BankUser.objects.get(user=request.user)
    except models.BankUser.DoesNotExist:
        context = {'msg': 'not authenticated'}
        return render(request, 'error.html', context, status=401)

    # active bank user
    if login_bankuser.state == 'INACTIVE':
        context = {'msg': 'not active BankUser'}
        return render(request, 'error.html', context, status=400)

    # check if a valid request
    f = form.HandleRequestForm(request.POST)
    if not f.is_valid():
        context = {'msg': 'not valid request ', 'form': f}
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
    try:
        from_bankuser = models.BankUser.objects.get(id=inner_request.from_id)
    except models.BankUser.DoesNotExist:
        from_bankuser = None

    try:
        to_bankuser = models.BankUser.objects.get(id=inner_request.to_id)
    except models.BankUser.DoesNotExist:
        to_bankuser = None

    print('-'*50)
    print(login_bankuser.user_type)
    print('-'*50)

    # ADMIN
    if login_bankuser.user_type == 'ADMIN':
        # ACCOUNT OPEN
        if inner_request.request == 'ACCOUNT_OPEN':
            if to_bankuser.user_type in ['TIER2', 'TIER1']:
                if int(request.POST['approve']):
                    # update bank_user
                    to_bankuser.state = 'ACTIVE'
                    to_bankuser.save()
                    inner_request.state = 'APPROVED'
                    inner_request.save()
                    context['msg'] = 'APPROVED'
                    return render(request, 'success.html', context)
                else:
                    inner_request.state = 'DECLINED'
                    inner_request.save()
                    context['msg'] = 'DECLINED'
                    return render(request, 'success.html', context)
            else:
                context = {'msg': 'admin can only approve tier2, tie1 account open'}
                return render(request, 'error.html', context, status=401)

        # ACCOUNT UPDATE
        elif inner_request.request == 'ACCOUNT_UPDATE':
            if to_bankuser.user_type in ['ADMIN', 'TIER2', 'TIER1']:
                if int(request.POST['approve']):
                    # check phone
                    if inner_request.phone and inner_request.phone != to_bankuser.phone:
                        try:
                            _ = models.BankUser.objects.get(phone=inner_request.phone)
                            context = {'msg': 'DECLINE ONLY, phone exist'}
                            return render(request, 'error.html', context, status=400)
                        except models.BankUser.DoesNotExist:
                            pass
                    # check email
                    if inner_request.email and inner_request.email != to_bankuser.email:
                        try:
                            _ = models.BankUser.objects.get(email=inner_request.email)
                            context = {'msg': 'DECLINE ONLY, email exist'}
                            return render(request, 'error.html', context, status=400)
                        except models.BankUser.DoesNotExist:
                            pass
                    # update bank_user
                    if inner_request.phone:
                        to_bankuser.phone = inner_request.phone
                    if inner_request.email:
                        to_bankuser.email = inner_request.email
                    if inner_request.address:
                        to_bankuser.address = inner_request.address
                    to_bankuser.save()
                    inner_request.state = 'APPROVED'
                    inner_request.save()
                    context['msg'] = 'APPROVED'
                    return render(request, 'success.html', context)
                else:
                    inner_request.state = 'DECLINED'
                    inner_request.save()
                    context['msg'] = 'DECLINED'
                    return render(request, 'success.html', context, status=401)
            else:
                context = {'msg': 'admin can only approve admin, tier2, tie1 account update'}
                return render(request, 'error.html', context, status=401)
        else:
            context['msg'] = 'admin can only approve or decline internal account open/update/delete'
            return render(request, 'error.html', context, status=401)
    elif login_bankuser.user_type == 'TIER2':
        # ACCOUNT OPEN
        if inner_request.request == 'ACCOUNT_OPEN':
            if to_bankuser.user_type in ['CUSTOMER', 'MERCHANT']:
                if int(request.POST['approve']):
                    # update bank_user
                    to_bankuser.state = 'ACTIVE'
                    to_bankuser.save()
                    inner_request.state = 'APPROVED'
                    inner_request.save()
                    context['msg'] = 'APPROVED'
                    return render(request, 'success.html', context)
                else:
                    inner_request.state = 'DECLINED'
                    inner_request.save()
                    context['msg'] = 'DECLINED'
                    return render(request, 'success.html', context, status=401)
            else:
                context = {'msg': 'tier2 can only approve customer, merchant account open'}
                return render(request, 'error.html', context, status=401)
        # ACCOUNT UPDATE
        elif inner_request.request == 'ACCOUNT_UPDATE':
            if to_bankuser.user_type in ['CUSTOMER', 'MERCHANT']:
                if int(request.POST['approve']):
                    # check phone
                    if inner_request.phone and inner_request.phone != to_bankuser.phone:
                        try:
                            _ = models.BankUser.objects.get(phone=inner_request.phone)
                            context = {'msg': 'DECLINE ONLY, phone exist'}
                            return render(request, 'error.html', context, status=400)
                        except models.BankUser.DoesNotExist:
                            pass
                    # check email
                    if inner_request.email and inner_request.email != to_bankuser.email:
                        try:
                            _ = models.BankUser.objects.get(email=inner_request.email)
                            context = {'msg': 'DECLINE ONLY, email exist'}
                            return render(request, 'error.html', context, status=400)
                        except models.BankUser.DoesNotExist:
                            pass
                    # update bank_user
                    if inner_request.phone:
                        to_bankuser.phone = inner_request.phone
                    if inner_request.email:
                        to_bankuser.email = inner_request.email
                    if inner_request.address:
                        to_bankuser.address = inner_request.address
                    to_bankuser.save()
                    inner_request.state = 'APPROVED'
                    inner_request.save()
                    context['msg'] = 'APPROVED'
                    return render(request, 'success.html', context)
                else:
                    inner_request.state = 'DECLINED'
                    inner_request.save()
                    context['msg'] = 'DECLINED'
                    return render(request, 'success.html', context, status=401)
            else:
                context = {'msg': 'tier1 can only approve customer, merchant account update'}
                return render(request, 'error.html', context, status=401)
        elif inner_request.request == 'APPROVE_REQUEST':
            # get request
            try:
                target_inner_request = models.Request.objects.get(id=inner_request.request_id)
            except models.Request.DoesNotExist:
                context = {'msg': 'target request not found'}
                return render(request, 'error.html', context, status=401)

            if int(request.POST['approve']):
                # 'WAITING_T2', 'WAITING_T2_EX', 'WAITING_EX', 'WAITING'
                if target_inner_request.sub_state == 'WAITING_T2':
                    target_inner_request.sub_state = 'WAITING'

                if target_inner_request.sub_state == 'WAITING_T2_EX':
                    target_inner_request.sub_state = 'WAITING_EX'
                target_inner_request.save()

                inner_request.state = 'APPROVED'
                inner_request.save()

                context = {'msg': 'APPROVE'}
                return render(request, 'success.html', context, status=200)
            else:

                inner_request.state = 'DECLINED'
                inner_request.save()

                context = {'msg': 'Decline'}
                return render(request, 'success.html', context, status=200)

        else:
            context['msg'] = 't2 can only approve or decline internal account open/update/delete, approve_request'
    # TIER1
    elif login_bankuser.user_type == 'TIER1':
        # ACCOUNT OPEN
        if inner_request.request == 'ACCOUNT_OPEN':
            if to_bankuser.user_type in ['CUSTOMER', 'MERCHANT']:
                if int(request.POST['approve']):
                    # sub-state waiting
                    if inner_request.sub_state != 'WAITING':
                        context['msg'] = 'DECLINED sub-state is not waiting'
                        return render(request, 'error.html', context, status=400)
                    # update bank_user
                    to_bankuser.state = 'ACTIVE'
                    to_bankuser.save()
                    inner_request.state = 'APPROVED'
                    inner_request.save()
                    context['msg'] = 'APPROVED'
                    return render(request, 'success.html', context)
                else:
                    inner_request.state = 'DECLINED'
                    inner_request.save()
                    context['msg'] = 'DECLINED'
                    return render(request, 'success.html', context, status=401)
            else:
                context = {'msg': 'tier1 can only approve customer, merchant account open'}
                return render(request, 'error.html', context, status=401)
        # ACCOUNT UPDATE
        elif inner_request.request == 'ACCOUNT_UPDATE':
            if to_bankuser.user_type in ['CUSTOMER', 'MERCHANT']:
                if int(request.POST['approve']):
                    # sub-state waiting
                    if inner_request.sub_state != 'WAITING':
                        context['msg'] = 'DECLINED sub-state is not waiting'
                        return render(request, 'error.html', context, status=400)
                    # check phone
                    if inner_request.phone and inner_request.phone != to_bankuser.phone:
                        try:
                            _ = models.BankUser.objects.get(phone=inner_request.phone)
                            context = {'msg': 'DECLINE ONLY, phone exist'}
                            return render(request, 'error.html', context, status=400)
                        except models.BankUser.DoesNotExist:
                            pass
                    # check email
                    if inner_request.email and inner_request.email != to_bankuser.email:
                        try:
                            _ = models.BankUser.objects.get(email=inner_request.email)
                            context = {'msg': 'DECLINE ONLY, email exist'}
                            return render(request, 'error.html', context, status=400)
                        except models.BankUser.DoesNotExist:
                            pass
                    # update bank_user
                    if inner_request.phone:
                        to_bankuser.phone = inner_request.phone
                    if inner_request.email:
                        to_bankuser.email = inner_request.email
                    if inner_request.address:
                        to_bankuser.address = inner_request.address
                    to_bankuser.save()
                    inner_request.state = 'APPROVED'
                    inner_request.save()
                    context['msg'] = 'APPROVED'
                    return render(request, 'success.html', context)
                else:
                    inner_request.state = 'DECLINED'
                    inner_request.save()
                    context['msg'] = 'DECLINED'
                    return render(request, 'success.html', context, status=401)
            else:
                context = {'msg': 'tier1 can only approve customer, merchant account update'}
                return render(request, 'error.html', context, status=401)
        else:
            context['msg'] = 't1 can only approve or decline internal account open/update/delete'
            return render(request, 'error.html', context, status=401)
    elif login_bankuser.user_type == 'MERCHANT':
        if inner_request.request == 'APPROVE_REQUEST':
            # get request
            try:
                target_inner_request = models.Request.objects.get(id=inner_request.request_id)
            except models.Request.DoesNotExist:
                context = {'msg': 'target request not found'}
                return render(request, 'error.html', context, status=401)

            if int(request.POST['approve']):
                # 'WAITING_T2', 'WAITING_T2_EX', 'WAITING_EX', 'WAITING'
                if target_inner_request.sub_state == 'WAITING_EX':
                    target_inner_request.sub_state = 'WAITING'

                if target_inner_request.sub_state == 'WAITING_T2_EX':
                    target_inner_request.sub_state = 'WAITING_T2'
                target_inner_request.save()

                inner_request.state = 'APPROVED'
                inner_request.save()

                context = {'msg': 'APPROVE'}
                return render(request, 'success.html', context, status=200)
            else:

                inner_request.state = 'DECLINED'
                inner_request.save()

                context = {'msg': 'Decline'}
                return render(request, 'success.html', context, status=200)
        else:
            context = {'msg': 'customer can only approve'}
            return render(request, 'error.html', context, status=401)
    elif login_bankuser.user_type == 'CUSTOMER':
        if inner_request.request == 'APPROVE_REQUEST':
            # get request
            try:
                target_inner_request = models.Request.objects.get(id=inner_request.request_id)
            except models.Request.DoesNotExist:
                context = {'msg': 'target request not found'}
                return render(request, 'error.html', context, status=401)

            if int(request.POST['approve']):
                # 'WAITING_T2', 'WAITING_T2_EX', 'WAITING_EX', 'WAITING'
                if target_inner_request.sub_state == 'WAITING_EX':
                    target_inner_request.sub_state = 'WAITING'

                if target_inner_request.sub_state == 'WAITING_T2_EX':
                    target_inner_request.sub_state = 'WAITING_T2'
                target_inner_request.save()

                inner_request.state = 'APPROVED'
                inner_request.save()

                context = {'msg': 'APPROVE'}
                return render(request, 'success.html', context, status=200)
            else:

                inner_request.state = 'DECLINED'
                inner_request.save()

                context = {'msg': 'Decline'}
                return render(request, 'success.html', context, status=200)
        else:
            context = {'msg': 'customer can only approve'}
            return render(request, 'error.html', context, status=401)
    context['msg'] = 'UNKNOWN'
    return render(request, 'error.html', context, status=401)
