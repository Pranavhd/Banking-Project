from django.shortcuts import render, redirect
import datetime
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from . import form
from . import models
import collections
from django.db.models import Q
import random
import string
import decimal


RenderUser = collections.namedtuple(
    'RenderUser', 'username user_type state id email phone address credit_balance checking_balance saving_balance credit_number cvv')
RenderAccountOpenRequest = collections.namedtuple(
    'RenderAccountOpenRequest', 'from_username to_username id state sub_state created request email phone address credit_balance checking_balance saving_balance')
RenderAccountUpdateRequest = collections.namedtuple(
    'RenderAccountUpdateRequest', 'from_username to_username id state sub_state created request email phone address')
RenderApproveRequest = collections.namedtuple(
    'RenderApproveRequest', 'from_username to_username id state sub_state target_state created request email phone address')
RenderFundRequest = collections.namedtuple(
    'RenderFundRequest', 'from_username to_username id state sub_state created request email phone address money critical')
RenderPaymentRequest = collections.namedtuple(
    'RenderPaymentRequest', 'from_username to_username id state sub_state created request email phone address money critical')
RenderLog = collections.namedtuple(
    'RenderLog', 'created msg')
RenderCreditPaymentRequest = collections.namedtuple(
    'RenderCreditPaymentRequest', 'created money')
RenderPenaltyRequest = collections.namedtuple(
    'RenderPenaltyRequest', 'created before_credit_balance interest late_fee after_credit_balance')


def count_user_penalty(user):
    now = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=3600*7)

    while (now - user.credit_balance_close_date).total_seconds() >= 30:

        user.credit_balance_close_date += datetime.timedelta(seconds=30)

        if user.credit_balance < 0:
            before_credit_balance = user.credit_balance
            after_credit_balance = float(user.credit_balance) * 1.02 - 20

            print(before_credit_balance, after_credit_balance)

            models.Request.objects.create(
                from_id=user.id,
                to_id=user.id,
                created=user.credit_balance_close_date,
                state='APPROVED',
                sub_state='WAITING',
                request='PENALTY',
                permission=0,
                user_type=user.user_type,
                request_id=-1,
                phone='',
                email='',
                address='',
                critical=0,
                money=0.0,
                from_balance='',
                to_balance='',
                credit_number='',
                cvv='',
                increment_credit_balance=0.0,
                increment_checking_balance=0.0,
                increment_saving_balance=0.0,
                before_credit_balance=before_credit_balance,
                interest=1.02,
                late_fee=20.0,
                after_credit_balance=after_credit_balance,
            )

        user.save()


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
            count_user_penalty(login_bankuser)
            return redirect('/customer/')
        elif login_bankuser.user_type == 'MERCHANT':
            count_user_penalty(login_bankuser)
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
        context = {'msg': 'not active BankUser whether deleted or not approved yet'}
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
        count_user_penalty(login_bankuser)
        return redirect('/customer/')
    elif login_bankuser.user_type == 'MERCHANT':
        count_user_penalty(login_bankuser)
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
    if not request.user.is_authenticated():
        context = {'msg': 'not authenticated'}
        return render(request, 'error.html', context, status=401)

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

    context = {'user_type': login_bankuser.user_type}
    return render(request, 'account_open.html', context)


def account_open_post_view(request):
    # valid user
    if not request.user.is_authenticated():
        context = {'msg': 'not authenticated'}
        return render(request, 'error.html', context, status=401)

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

    # create user
    user = User.objects.create_user(
        username=request.POST['username'],
        password=request.POST['password'],
    )

    credit_number = ''.join(random.choices(string.digits, k=16))
    cvv = ''.join(random.choices(string.digits, k=3))

    # create bank user
    bank_user = models.BankUser.objects.create(
        user=user,
        state='INACTIVE',
        user_type=request.POST['user_type'],
        username=request.POST['username'],
        phone=request.POST['phone'],
        email=request.POST['email'],
        address=request.POST['address'],
        credit_balance=request.POST['credit_balance'],
        checking_balance=request.POST['checking_balance'],
        saving_balance=request.POST['saving_balance'],
        credit_number=credit_number,
        cvv=cvv,
        credit_balance_close_date=datetime.datetime.now(),
    )

    # create request
    models.Request.objects.create(
        from_id=from_bankuser.id if from_bankuser else bank_user.id,
        to_id=bank_user.id,
        created=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=3600*7),
        state='PENDING',
        sub_state='WAITING_T2',
        request='ACCOUNT_OPEN',
        permission=0,
        user_type=request.POST['user_type'],
        request_id=-1,
        phone=request.POST['phone'],
        email=request.POST['email'],
        address=request.POST['address'],
        critical=0,
        money=0.0,
        from_balance='',
        to_balance='',
        credit_number=credit_number,
        cvv=cvv,
        increment_credit_balance=0.0,
        increment_checking_balance=0.0,
        increment_saving_balance=0.0,
        before_credit_balance=0.0,
        interest=0.0,
        late_fee=0.0,
        after_credit_balance=0.0,
    )

    # system log
    models.Log.objects.create(
        created=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=3600*7),
        msg='{} make ACCOUNT_OPEN request for {}'.format(from_bankuser.username, bank_user.username)
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
        to_bankuser = models.BankUser.objects.get(id=request.GET['id'])
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
        if to_bankuser.user_type in ['TIER2', 'TIER1', 'CUSTOMER', 'MERCHANT']:
            pass
        elif to_bankuser.id == from_bankuser.id:
            pass
        else:
            context = {'msg': 'tier2 only update self, t2, t1, customer, merchant'}
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
    context['user_type'] = from_bankuser.user_type
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
        to_bankuser = models.BankUser.objects.get(id=request.POST['id'])
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

    increment_credit_balance = request.POST.get('increment_credit_balance', 0.0)
    increment_checking_balance = request.POST.get('increment_checking_balance', 0.0)
    increment_saving_balance = request.POST.get('increment_saving_balance', 0.0)

    # ADMIN
    if from_bankuser.user_type == 'ADMIN':
        if to_bankuser.user_type not in ['TIER2', 'TIER1']:
            context = {'msg': 'admin only update tier2 tier1'}
            return render(request, 'error.html', context, status=401)
    # TIER2
    elif from_bankuser.user_type == 'TIER2':
        if to_bankuser.user_type in ['TIER2', 'TIER1', 'CUSTOMER', 'MERCHANT']:
            pass
        elif to_bankuser.id == from_bankuser.id:
            pass
        else:
            context = {'msg': 'tier1 only update tie2, tie1, customer, merchant'}
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
        increment_credit_balance = 0.0
        increment_checking_balance = 0.0
        increment_saving_balance = 0.0

    # create Request
    models.Request.objects.create(
        from_id=from_bankuser.id,
        to_id=to_bankuser.id,
        user_type=to_bankuser.user_type,
        created=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=3600*7),
        state='PENDING',
        sub_state=sub_state,
        request='ACCOUNT_UPDATE',
        permission=0,
        request_id=-1,
        phone=request.POST.get('phone', '').strip(),
        email=request.POST.get('email', '').strip(),
        address=request.POST.get('address', '').strip(),
        critical=0,
        money=0.0,
        from_balance='',
        to_balance='',
        increment_credit_balance=increment_credit_balance,
        increment_checking_balance=increment_checking_balance,
        increment_saving_balance=increment_saving_balance,
        before_credit_balance=0.0,
        interest=0.0,
        late_fee=0.0,
        after_credit_balance=0.0,
    )

    # system log
    models.Log.objects.create(
        created=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=3600*7),
        msg='{} make ACCOUNT_UPDATE request for {}'.format(from_bankuser.username, to_bankuser.username)
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
        to_bankuser = models.BankUser.objects.get(id=request.POST['id'])
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
        login_bankuser.address,
        login_bankuser.credit_balance,
        login_bankuser.checking_balance,
        login_bankuser.saving_balance,
        login_bankuser.credit_number,
        login_bankuser.cvv,
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
        if request.POST['from_email'] > 1000:
            context = {'msg': 't2 can not create critical transaction (above 1000)'}
            return render(request, 'error.html', context, status=400)
    elif login_bankuser.user_type == 'TIER1':
        pass
    elif login_bankuser.user_type == 'CUSTOMER':
        sub_state = 'WAITING_T2'
    elif login_bankuser.user_type == 'MERCHANT':
        sub_state = 'WAITING_T2'
    else:
        context = {'msg': 'unknown user'}
        return render(request, 'error.html', context, status=400)

    if login_bankuser.user_type in ['CUSTOMER', 'MERCHANT']:
        if login_bankuser.email != request.POST['from_email']:
            context = {'msg': 'customer can only send from their own email'}
            return render(request, 'error.html', context, status=401)
        from_bankuser = login_bankuser
    if login_bankuser.user_type in ['TIER2', 'TIER1']:
        try:
            from_bankuser = models.BankUser.objects.get(email=request.POST['from_email'])
        except models.BankUser.DoesNotExist:
            context = {'msg': 'from bank user not exist'}
            return render(request, 'error.html', context, status=401)
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

    if int(request.POST['money']) <= 0:
        context = {'msg': 'money must greate than 0'}
        return render(request, 'error.html', context, status=400)

    # create Request
    models.Request.objects.create(
        from_id=from_bankuser.id,
        to_id=to_bankuser.id if to_bankuser else -1,
        user_type='CUSTOMER',
        created=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=3600*7),
        state='PENDING',
        # sub-state for T1, 'WAITING_T2', 'WAITING_T2_EX', 'WAITING_EX', 'WAITING'
        sub_state=sub_state,
        request='FUND',
        request_id=-1,
        permission=-1,
        phone=request.POST.get('phone', '').strip(),
        email=request.POST.get('email', '').strip(),
        address=request.POST.get('address', '').strip(),
        critical=1 if int(request.POST['money']) > 1000 else 0,
        money=request.POST['money'],
        from_balance=request.POST['from_balance'],
        to_balance=request.POST['to_balance'],
        increment_credit_balance=0.0,
        increment_checking_balance=0.0,
        increment_saving_balance=0.0,
        before_credit_balance=0.0,
        interest=0.0,
        late_fee=0.0,
        after_credit_balance=0.0,
    )

    # system log
    models.Log.objects.create(
        created=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=3600*7),
        msg='{} make FUND request for {}'.format(from_bankuser.username, to_bankuser.username)
    )

    context = {'msg': 'TRANSFER REQUEST sent'}
    return render(request, 'success.html', context)


# ------ 5. payment -----
def make_payment_view(request):
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
    if login_bankuser.user_type != 'MERCHANT':
        context = {'msg': 'only merchant can make payment request'}
        return render(request, 'error.html', context, status=401)

    # active bank user
    if login_bankuser.state == 'INACTIVE':
        context = {'msg': 'not active BankUser'}
        return render(request, 'error.html', context, status=400)

    context = {}
    return render(request, 'make_payment.html', context)


def make_payment_post_view(request):
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
    if login_bankuser.user_type != 'MERCHANT':
        context = {'msg': 'only merchant can make payment request'}
        return render(request, 'error.html', context, status=401)

    # active bank user
    if login_bankuser.state == 'INACTIVE':
        context = {'msg': 'not active BankUser'}
        return render(request, 'error.html', context, status=400)

    from_bankuser = login_bankuser
    try:
        to_bankuser = models.BankUser.objects.get(credit_number=request.POST['credit_number'])
    except models.BankUser.DoesNotExist:
        context = {'msg': 'credit number/cvv not found'}
        return render(request, 'error.html', context, status=400)
    if to_bankuser.cvv != request.POST['cvv']:
        context = {'msg': 'credit number/cvv not found'}
        return render(request, 'error.html', context, status=400)
    if from_bankuser == to_bankuser:
        context = {'msg': 'can not be same user'}
        return render(request, 'error.html', context, status=400)
    if int(request.POST['money']) <= 0:
        context = {'msg': 'money must greater than 0'}
        return render(request, 'error.html', context, status=400)

    # create request
    models.Request.objects.create(
        from_id=from_bankuser.id,
        to_id=to_bankuser.id,
        created=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=3600*7),
        state='PENDING',
        sub_state='WAITING_T2',
        request='PAYMENT',
        permission=0,
        user_type=to_bankuser.user_type,
        request_id=-1,
        phone='',
        email='',
        address='',
        critical=1 if int(request.POST['money']) > 1000 else 0,
        money=request.POST['money'],
        from_balance='',
        to_balance='',
        credit_number=request.POST['credit_number'],
        cvv=request.POST['cvv'],
        increment_credit_balance=0.0,
        increment_checking_balance=0.0,
        increment_saving_balance=0.0,
        before_credit_balance=0.0,
        interest=0.0,
        late_fee=0.0,
        after_credit_balance=0.0,
    )

    # system log
    models.Log.objects.create(
        created=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=3600*7),
        msg='{} make PAYMENT request for {}'.format(from_bankuser.username, to_bankuser.username)
    )

    context = {'msg': 'Make Payment Request sent'}
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
        created=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=3600*7),
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
        money=0.0,
        from_balance='',
        to_balance='',
        increment_credit_balance=0.0,
        increment_checking_balance=0.0,
        increment_saving_balance=0.0,
        before_credit_balance=0.0,
        interest=0.0,
        late_fee=0.0,
        after_credit_balance=0.0,
    )

    # system log
    models.Log.objects.create(
        created=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=3600*7),
        msg='{} make APPROVE_REQUEST request for {}'.format(from_bankuser.username, to_bankuser.username)
    )

    context = {'msg': 'APPROVE REQUEST sent'}
    return render(request, 'success.html', context)


# 8. --- Credit Payment ---
def make_credit_payment_post_view(request):

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

    # customer
    if login_bankuser.user_type != 'CUSTOMER':
        context = {'msg': 'only customer can make credit payment'}
        return render(request, 'error.html', context, status=400)

    if login_bankuser.credit_balance >= 0:
        context = {'msg': 'you have enough credit, you dont have to pay bill'}
        return render(request, 'error.html', context, status=400)

    if login_bankuser.checking_balance + login_bankuser.credit_balance < 0:
        context = {'msg': 'the balance in checking is not enough'}
        return render(request, 'error.html', context, status=400)

    # create Request
    models.Request.objects.create(
        from_id=login_bankuser.id,
        to_id=login_bankuser.id if login_bankuser else -1,
        user_type=login_bankuser.user_type,
        created=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=3600*7),
        state='APPROVED',
        # sub-state for T1, 'WAITING_T2', 'WAITING_T2_EX', 'WAITING_EX', 'WAITING'
        sub_state='WAITING',
        request='CREDIT_PAYMENT',
        request_id=-1,
        permission=0,
        critical=0,
        phone='',
        email='',
        address='',
        money=abs(login_bankuser.credit_balance),
        from_balance='',
        to_balance='',
        increment_credit_balance=0.0,
        increment_checking_balance=0.0,
        increment_saving_balance=0.0,
        before_credit_balance=0.0,
        interest=0.0,
        late_fee=0.0,
        after_credit_balance=0.0,
    )

    login_bankuser.checking_balance += login_bankuser.credit_balance
    login_bankuser.credit_balance = 0
    login_bankuser.save()

    # system log
    models.Log.objects.create(
        created=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=3600*7),
        msg='{} make CREDIT PAYMENT'.format(login_bankuser.username)
    )

    context = {'msg': 'you make credit payment'}
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
        'logs': []
    }

    # render user
    user = RenderUser(
        login_bankuser.username,
        login_bankuser.user_type,
        login_bankuser.state,
        login_bankuser.id,
        login_bankuser.email,
        login_bankuser.phone,
        login_bankuser.address,
        login_bankuser.credit_balance,
        login_bankuser.checking_balance,
        login_bankuser.saving_balance,
        login_bankuser.credit_number,
        login_bankuser.cvv,
    )
    context['user'] = user

    # render users
    users = models.BankUser.objects.all(
    ).exclude(user_type='ADMIN').exclude(
        user_type='CUSTOMER').exclude(
        user_type='MERCHANT')
    for u in users:
        count_user_penalty(u)
        context['users'].append(RenderUser(
            u.username,
            u.user_type,
            u.state,
            u.id,
            u.email,
            u.phone,
            u.address,
            u.credit_balance,
            u.checking_balance,
            u.saving_balance,
            u.credit_number,
            u.cvv,
        ))

    # render logs
    logs = models.Log.objects.all()
    for log in logs:
        context['logs'].append(RenderLog(log.created, log.msg))

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
                    inner_request.address,
                    to_bank_user.credit_balance,
                    to_bank_user.checking_balance,
                    to_bank_user.saving_balance,
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
        login_bankuser.address,
        login_bankuser.credit_balance,
        login_bankuser.checking_balance,
        login_bankuser.saving_balance,
        login_bankuser.credit_number,
        login_bankuser.cvv,
    )
    context['user'] = user

    # render users
    users = models.BankUser.objects.all(
    ).exclude(user_type='ADMIN')

    for u in users:
        count_user_penalty(u)
        context['users'].append(RenderUser(u.username, u.user_type, u.state, u.id, '***', '***', '***', '***', '***', '***', '***', '***'))

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
                    inner_request.address,
                    to_bank_user.credit_balance,
                    to_bank_user.checking_balance,
                    to_bank_user.saving_balance,
                ))

        # ACCOUNT UPDATE
        if inner_request.request == 'ACCOUNT_UPDATE':
            if to_bank_user.user_type in ['TIER2', 'TIER1', 'CUSTOMER', 'MERCHANT']:
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
                    inner_request.address,
                ))

        # FUND
        if inner_request.request == 'FUND':
            if to_bank_user.user_type in ['CUSTOMER', 'MERCHANT']:
                context['fund_requests'].append(RenderFundRequest(
                    from_bank_user.username if from_bank_user else 'obsolete user',
                    to_bank_user.username if to_bank_user else 'obsolete user',
                    inner_request.id,
                    inner_request.state,
                    inner_request.sub_state,
                    inner_request.created,
                    inner_request.request,
                    inner_request.email,
                    inner_request.phone,
                    inner_request.address,
                    inner_request.money,
                    inner_request.critical
                ))

        # PAYMENT
        if inner_request.request == 'PAYMENT':
            if to_bank_user.user_type in ['CUSTOMER', 'MERCHANT']:
                context['payment_requests'].append(RenderPaymentRequest(
                    from_bank_user.username if from_bank_user else 'obsolete user',
                    to_bank_user.username if to_bank_user else 'obsolete user',
                    inner_request.id,
                    inner_request.state,
                    inner_request.sub_state,
                    inner_request.created,
                    inner_request.request,
                    inner_request.email,
                    inner_request.phone,
                    inner_request.address,
                    inner_request.money,
                    inner_request.critical
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
        login_bankuser.address,
        login_bankuser.credit_balance,
        login_bankuser.checking_balance,
        login_bankuser.saving_balance,
        login_bankuser.credit_number,
        login_bankuser.cvv,

    )
    context['user'] = user

    # render users
    users = models.BankUser.objects.all(
    ).exclude(user_type='ADMIN').exclude(
        user_type='TIER2').exclude(
        user_type='TIER1')
    for u in users:
        count_user_penalty(u)
        context['users'].append(RenderUser(u.username, u.user_type, u.state, u.id, '***', '***', '***', '***', '***', '***', '***', '***'))

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
                    inner_request.address,
                    to_bank_user.credit_balance,
                    to_bank_user.checking_balance,
                    to_bank_user.saving_balance,
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

        # FUND
        if inner_request.request == 'FUND':
            if to_bank_user.user_type in ['CUSTOMER', 'MERCHANT']:
                context['fund_requests'].append(RenderFundRequest(
                    from_bank_user.username if from_bank_user else 'obsolete user',
                    to_bank_user.username if to_bank_user else 'obsolete user',
                    inner_request.id,
                    inner_request.state,
                    inner_request.sub_state,
                    inner_request.created,
                    inner_request.request,
                    inner_request.email,
                    inner_request.phone,
                    inner_request.address,
                    inner_request.money,
                    inner_request.critical
                ))

        # PAYMENT
        if inner_request.request == 'PAYMENT':
            if to_bank_user.user_type in ['CUSTOMER', 'MERCHANT']:
                context['payment_requests'].append(RenderPaymentRequest(
                    from_bank_user.username if from_bank_user else 'obsolete user',
                    to_bank_user.username if to_bank_user else 'obsolete user',
                    inner_request.id,
                    inner_request.state,
                    inner_request.sub_state,
                    inner_request.created,
                    inner_request.request,
                    inner_request.email,
                    inner_request.phone,
                    inner_request.address,
                    inner_request.money,
                    inner_request.critical
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

    count_user_penalty(login_bankuser)

    context = {
        'user': None,
        'users': [],
        'account_open_requests': [],
        'account_update_requests': [],
        'approve_requests': [],
        'fund_requests': [],
        'payment_requests': [],
        'credit_payment_requests': [],
        'penalty_requests': [],
    }

    # render user
    user = RenderUser(
        login_bankuser.username,
        login_bankuser.user_type,
        login_bankuser.state,
        login_bankuser.id,
        login_bankuser.email,
        login_bankuser.phone,
        login_bankuser.address,
        login_bankuser.credit_balance,
        login_bankuser.checking_balance,
        login_bankuser.saving_balance,
        login_bankuser.credit_number,
        login_bankuser.cvv,
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

        # CREDIT PAYMENT REQUEST
        if inner_request.request == 'CREDIT_PAYMENT':
            if inner_request.to_id == login_bankuser.id:
                context['credit_payment_requests'].append(RenderCreditPaymentRequest(
                    inner_request.created,
                    inner_request.money,
                ))

        # PENALTY REQUEST
        if inner_request.request == 'PENALTY':
            if inner_request.to_id == login_bankuser.id:
                context['penalty_requests'].append(RenderPenaltyRequest(
                    inner_request.created,
                    inner_request.before_credit_balance,
                    inner_request.interest,
                    inner_request.late_fee,
                    inner_request.after_credit_balance,
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

    count_user_penalty(login_bankuser)

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
        login_bankuser.address,
        login_bankuser.credit_balance,
        login_bankuser.checking_balance,
        login_bankuser.saving_balance,
        login_bankuser.credit_number,
        login_bankuser.cvv,
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
            if to_bankuser.user_type in ['TIER2', 'TIER1', 'CUSTOMER', 'MERCHANT']:
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
                    if inner_request.increment_credit_balance:
                        to_bankuser.credit_balance += inner_request.increment_credit_balance
                    if inner_request.increment_checking_balance:
                        to_bankuser.checking_balance += inner_request.increment_checking_balance
                    if inner_request.increment_saving_balance:
                        to_bankuser.saving_balance = inner_request.increment_saving_balance

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
                context = {'msg': 'tier2 can only approve tier2, tier1, customer, merchant account update'}
                return render(request, 'error.html', context, status=401)
        # APPROVE
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
        elif inner_request.request == 'FUND':
            if int(request.POST['approve']):

                # count balance
                if inner_request.from_balance == 'CREDIT' and inner_request.to_balance == 'CREDIT':
                    if from_bankuser.credit_balance < inner_request.money:
                        context['msg'] = 'balance not enough'
                        return render(request, 'error.html', context, status=400)
                    if from_bankuser == to_bankuser:
                        from_bankuser.credit_balance -= inner_request.money
                        from_bankuser.credit_balance += inner_request.money
                        from_bankuser.save()
                    else:
                        from_bankuser.credit_balance -= inner_request.money
                        from_bankuser.save()
                        to_bankuser.credit_balance += inner_request.money
                        to_bankuser.save()

                if inner_request.from_balance == 'CREDIT' and inner_request.to_balance == 'CHECKING':
                    if from_bankuser.credit_balance < inner_request.money:
                        context['msg'] = 'balance not enough'
                        return render(request, 'error.html', context, status=400)
                    if from_bankuser == to_bankuser:
                        from_bankuser.credit_balance -= inner_request.money
                        from_bankuser.checking_balance += inner_request.money
                        from_bankuser.save()
                    else:
                        from_bankuser.credit_balance -= inner_request.money
                        from_bankuser.save()
                        to_bankuser.checking_balance += inner_request.money
                        to_bankuser.save()
                if inner_request.from_balance == 'CREDIT' and inner_request.to_balance == 'SAVING':
                    if from_bankuser.credit_balance < inner_request.money:
                        context['msg'] = 'balance not enough'
                        return render(request, 'error.html', context, status=400)
                    if from_bankuser == to_bankuser:
                        from_bankuser.credit_balance -= inner_request.money
                        from_bankuser.saving_balance += inner_request.money
                        from_bankuser.save()
                    else:
                        from_bankuser.credit_balance -= inner_request.money
                        from_bankuser.save()
                        to_bankuser.saving_balance += inner_request.money
                        to_bankuser.save()

                if inner_request.from_balance == 'CHECKING' and inner_request.to_balance == 'CREDIT':
                    if from_bankuser.checking_balance < inner_request.money:
                        context['msg'] = 'balance not enough'
                        return render(request, 'error.html', context, status=400)
                    if from_bankuser == to_bankuser:
                        from_bankuser.checking_balance -= inner_request.money
                        from_bankuser.credit_balance += inner_request.money
                        from_bankuser.save()
                    else:
                        from_bankuser.checking_balance -= inner_request.money
                        from_bankuser.save()
                        to_bankuser.credit_balance += inner_request.money
                        to_bankuser.save()

                if inner_request.from_balance == 'CHECKING' and inner_request.to_balance == 'CHECKING':
                    if from_bankuser.checking_balance < inner_request.money:
                        context['msg'] = 'balance not enough'
                        return render(request, 'error.html', context, status=400)
                    if from_bankuser == to_bankuser:
                        from_bankuser.checking_balance -= inner_request.money
                        from_bankuser.checking_balance += inner_request.money
                        from_bankuser.save()
                    else:
                        from_bankuser.checking_balance -= inner_request.money
                        from_bankuser.save()
                        to_bankuser.checking_balance += inner_request.money
                        to_bankuser.save()

                if inner_request.from_balance == 'CHECKING' and inner_request.to_balance == 'SAVING':
                    if from_bankuser.checking_balance < inner_request.money:
                        context['msg'] = 'balance not enough'
                        return render(request, 'error.html', context, status=400)
                    if from_bankuser == to_bankuser:
                        from_bankuser.checking_balance -= inner_request.money
                        from_bankuser.saving_balance += inner_request.money
                        from_bankuser.save()
                    else:
                        from_bankuser.checking_balance -= inner_request.money
                        from_bankuser.save()
                        to_bankuser.saving_balance += inner_request.money
                        to_bankuser.save()

                if inner_request.from_balance == 'SAVING' and inner_request.to_balance == 'CREDIT':
                    if from_bankuser.saving_balance < inner_request.money:
                        context['msg'] = 'balance not enough'
                        return render(request, 'error.html', context, status=400)
                    if from_bankuser == to_bankuser:
                        from_bankuser.saving_balance -= inner_request.money
                        from_bankuser.credit_balance += inner_request.money
                        from_bankuser.save()
                    else:
                        from_bankuser.saving_balance -= inner_request.money
                        from_bankuser.save()
                        to_bankuser.credit_balance += inner_request.money
                        to_bankuser.save()

                if inner_request.from_balance == 'SAVING' and inner_request.to_balance == 'CHECKING':
                    if from_bankuser.saving_balance < inner_request.money:
                        context['msg'] = 'balance not enough'
                        return render(request, 'error.html', context, status=400)
                    if from_bankuser == to_bankuser:
                        from_bankuser.saving_balance -= inner_request.money
                        from_bankuser.checking_balance += inner_request.money
                        from_bankuser.save()
                    else:
                        from_bankuser.saving_balance -= inner_request.money
                        from_bankuser.save()
                        to_bankuser.checking_balance += inner_request.money
                        to_bankuser.save()

                if inner_request.from_balance == 'SAVING' and inner_request.to_balance == 'SAVING':
                    if from_bankuser.saving_balance < inner_request.money:
                        context['msg'] = 'balance not enough'
                        return render(request, 'error.html', context, status=400)
                    if from_bankuser == to_bankuser:
                        from_bankuser.saving_balance -= inner_request.money
                        from_bankuser.saving_balance += inner_request.money
                        from_bankuser.save()
                    else:
                        from_bankuser.saving_balance -= inner_request.money
                        from_bankuser.save()
                        to_bankuser.saving_balance += inner_request.money
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
        elif inner_request.request == 'PAYMENT':
            if int(request.POST['approve']):

                if to_bankuser.credit_balance + 1000 < inner_request.money:
                    context['msg'] = 'to bank user balance not enough'
                    return render(request, 'error.html', context, status=400)

                from_bankuser.credit_balance += inner_request.money
                from_bankuser.save()
                to_bankuser.credit_balance -= inner_request.money
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
                    if inner_request.increment_credit_balance:
                        to_bankuser.credit_balance += inner_request.increment_credit_balance
                    if inner_request.increment_checking_balance:
                        to_bankuser.checking_balance += inner_request.increment_checking_balance
                    if inner_request.increment_saving_balance:
                        to_bankuser.saving_balance = inner_request.increment_saving_balance

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
        # FUND
        elif inner_request.request == 'FUND':
            if int(request.POST['approve']):
                # sub-state waiting
                if inner_request.sub_state != 'WAITING':
                    context['msg'] = 'DECLINED sub-state is not waiting'
                    return render(request, 'error.html', context, status=400)
                if inner_request.critical:
                    context['msg'] = 't1 can not approve critical'
                    return render(request, 'error.html', context, status=400)

                # count balance
                if inner_request.from_balance == 'CREDIT' and inner_request.to_balance == 'CREDIT':
                    if from_bankuser.credit_balance < inner_request.money:
                        context['msg'] = 'balance not enough'
                        return render(request, 'error.html', context, status=400)
                    if from_bankuser == to_bankuser:
                        from_bankuser.credit_balance -= inner_request.money
                        from_bankuser.credit_balance += inner_request.money
                        from_bankuser.save()
                    else:
                        from_bankuser.credit_balance -= inner_request.money
                        from_bankuser.save()
                        to_bankuser.credit_balance += inner_request.money
                        to_bankuser.save()

                if inner_request.from_balance == 'CREDIT' and inner_request.to_balance == 'CHECKING':
                    if from_bankuser.credit_balance < inner_request.money:
                        context['msg'] = 'balance not enough'
                        return render(request, 'error.html', context, status=400)
                    if from_bankuser == to_bankuser:
                        from_bankuser.credit_balance -= inner_request.money
                        from_bankuser.checking_balance += inner_request.money
                        from_bankuser.save()
                    else:
                        from_bankuser.credit_balance -= inner_request.money
                        from_bankuser.save()
                        to_bankuser.checking_balance += inner_request.money
                        to_bankuser.save()
                if inner_request.from_balance == 'CREDIT' and inner_request.to_balance == 'SAVING':
                    if from_bankuser.credit_balance < inner_request.money:
                        context['msg'] = 'balance not enough'
                        return render(request, 'error.html', context, status=400)
                    if from_bankuser == to_bankuser:
                        from_bankuser.credit_balance -= inner_request.money
                        from_bankuser.saving_balance += inner_request.money
                        from_bankuser.save()
                    else:
                        from_bankuser.credit_balance -= inner_request.money
                        from_bankuser.save()
                        to_bankuser.saving_balance += inner_request.money
                        to_bankuser.save()

                if inner_request.from_balance == 'CHECKING' and inner_request.to_balance == 'CREDIT':
                    if from_bankuser.checking_balance < inner_request.money:
                        context['msg'] = 'balance not enough'
                        return render(request, 'error.html', context, status=400)
                    if from_bankuser == to_bankuser:
                        from_bankuser.checking_balance -= inner_request.money
                        from_bankuser.credit_balance += inner_request.money
                        from_bankuser.save()
                    else:
                        from_bankuser.checking_balance -= inner_request.money
                        from_bankuser.save()
                        to_bankuser.credit_balance += inner_request.money
                        to_bankuser.save()

                if inner_request.from_balance == 'CHECKING' and inner_request.to_balance == 'CHECKING':
                    if from_bankuser.checking_balance < inner_request.money:
                        context['msg'] = 'balance not enough'
                        return render(request, 'error.html', context, status=400)
                    if from_bankuser == to_bankuser:
                        from_bankuser.checking_balance -= inner_request.money
                        from_bankuser.checking_balance += inner_request.money
                        from_bankuser.save()
                    else:
                        from_bankuser.checking_balance -= inner_request.money
                        from_bankuser.save()
                        to_bankuser.checking_balance += inner_request.money
                        to_bankuser.save()

                if inner_request.from_balance == 'CHECKING' and inner_request.to_balance == 'SAVING':
                    if from_bankuser.checking_balance < inner_request.money:
                        context['msg'] = 'balance not enough'
                        return render(request, 'error.html', context, status=400)
                    if from_bankuser == to_bankuser:
                        from_bankuser.checking_balance -= inner_request.money
                        from_bankuser.saving_balance += inner_request.money
                        from_bankuser.save()
                    else:
                        from_bankuser.checking_balance -= inner_request.money
                        from_bankuser.save()
                        to_bankuser.saving_balance += inner_request.money
                        to_bankuser.save()

                if inner_request.from_balance == 'SAVING' and inner_request.to_balance == 'CREDIT':
                    if from_bankuser.saving_balance < inner_request.money:
                        context['msg'] = 'balance not enough'
                        return render(request, 'error.html', context, status=400)
                    if from_bankuser == to_bankuser:
                        from_bankuser.saving_balance -= inner_request.money
                        from_bankuser.credit_balance += inner_request.money
                        from_bankuser.save()
                    else:
                        from_bankuser.saving_balance -= inner_request.money
                        from_bankuser.save()
                        to_bankuser.credit_balance += inner_request.money
                        to_bankuser.save()

                if inner_request.from_balance == 'SAVING' and inner_request.to_balance == 'CHECKING':
                    if from_bankuser.saving_balance < inner_request.money:
                        context['msg'] = 'balance not enough'
                        return render(request, 'error.html', context, status=400)
                    if from_bankuser == to_bankuser:
                        from_bankuser.saving_balance -= inner_request.money
                        from_bankuser.checking_balance += inner_request.money
                        from_bankuser.save()
                    else:
                        from_bankuser.saving_balance -= inner_request.money
                        from_bankuser.save()
                        to_bankuser.checking_balance += inner_request.money
                        to_bankuser.save()

                if inner_request.from_balance == 'SAVING' and inner_request.to_balance == 'SAVING':
                    if from_bankuser.saving_balance < inner_request.money:
                        context['msg'] = 'balance not enough'
                        return render(request, 'error.html', context, status=400)
                    if from_bankuser == to_bankuser:
                        from_bankuser.saving_balance -= inner_request.money
                        from_bankuser.saving_balance += inner_request.money
                        from_bankuser.save()
                    else:
                        from_bankuser.saving_balance -= inner_request.money
                        from_bankuser.save()
                        to_bankuser.saving_balance += inner_request.money
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
        # PAYMENT
        elif inner_request.request == 'PAYMENT':
            if int(request.POST['approve']):
                # sub-state waiting
                if inner_request.sub_state != 'WAITING':
                    context['msg'] = 'DECLINED sub-state is not waiting'
                    return render(request, 'error.html', context, status=400)
                if inner_request.critical:
                    context['msg'] = 't1 can not approve critical'
                    return render(request, 'error.html', context, status=400)

                if to_bankuser.credit_balance + 1000 < inner_request.money:
                    context['msg'] = 'to bank user balance not enough'
                    return render(request, 'error.html', context, status=400)

                from_bankuser.credit_balance += inner_request.money
                from_bankuser.save()
                to_bankuser.credit_balance -= inner_request.money
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
