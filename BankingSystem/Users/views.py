from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from . import models
from . import forms
from .form import UpdatePersonalDetailsForm

# Create your views here.

def create_internal_user(request):
    # check if a valid user
    if not request.user.is_authenticated():
        return HttpResponse(status=401)

    # check if it is an admin user
    try:
        employee = models.Employee.objects.get(user=request.user)
    except models.Employee.DoesNotExist:
        return HttpResponse(status=401)
    if employee.level != 0:
        return HttpResponse(status=401)

    # check POST data is valid
    f = forms.CreateUserForm(request.POST)
    if not f.is_valid():
        return HttpResponse(status=400)

    # check if username already exist
    try:
        _ = User.objects.get(username=request.POST['username'])
        return HttpResponse(status=400)
    except User.DoesNotExist:
        pass

    # create a new employee
    user = User.objects.create_user(
        username=request.POST['username'],
        email=request.POST['email'],
        password=request.POST['password']
    )
    _ = models.Employee.objects.create(user=user, level=request.POST['level'])
    return HttpResponse(status=201)


def update_internal_user(request):
    # check if a valid user
    if not request.user.is_authenticated():
        return HttpResponse(status=401)

    # check if it is an admin user
    try:
        employee = models.Employee.objects.get(user=request.user)
    except models.Employee.DoesNotExist:
        return HttpResponse(status=401)
    if employee.level != 0:
        return HttpResponse(status=401)

    # check POST data is valid
    f = forms.UpdateUserForm(request.POST)
    if not f.is_valid():
        return HttpResponse(status=400)

    # check if username already exist
    try:
        user = User.objects.get(username=request.POST['username'])
    except User.DoesNotExist:
        return HttpResponse(status=400)

    # update user field
    user.email = request.POST['email'] if request.POST.get('email', None) else user.email
    user.password = request.POST['password'] if request.POST.get('password', None) else user.password
    user.save()
    return HttpResponse(status=201)


def delete_internal_user(request):
    # check if a valid user
    if not request.user.is_authenticated():
        return HttpResponse(status=401)

    # check if it is an admin user
    try:
        employee = models.Employee.objects.get(user=request.user)
    except models.Employee.DoesNotExist:
        return HttpResponse(status=401)
    if employee.level != 0:
        return HttpResponse(status=401)

    # check POST data is valid
    f = forms.DeleteUserForm(request.POST)
    if not f.is_valid():
        return HttpResponse(status=400)

    # check if username already exist
    try:
        user = User.objects.get(username=request.POST['username'])
    except User.DoesNotExist:
        return HttpResponse(status=400)
    del_employee = models.Employee.objects.get(user=user)
    del_employee.delete()
    user.delete()
    return HttpResponse(status=201)

# defining view for getting personal details information
def view_personal_details(request):
    user = User.objects.first()  # TODO: get the currently logged in user
    individual = models.Individual.objects.get(user=user)
    return render(request, 'personal_details.html', {'customer': individual})


# defining view for updating personal details information
def update_personal_details(request):
    user = User.objects.first()  # TODO: get the currently logged in user
    try:
        individual = models.Individual.objects.get(user=user)
        customer_id = individual.id
    except models.Individual.DoesNotExist:
        return HttpResponse(status=400)

    # update customer details
    if request.method == "POST":
        form = UpdatePersonalDetailsForm(data=request.POST)
        if not form.is_valid():
            return HttpResponse(status=400)

        if form.is_valid():
            user.email = form.cleaned_data['email']
            user.username = form.cleaned_data['username']
            individual.mail_address = form.cleaned_data['mail_address']
            user.save()
            individual.save()
    return HttpResponse(status=201)
