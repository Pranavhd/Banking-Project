from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from . import form
from . import models


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
    f = form.CreateUserForm(request.POST)
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
    # TODO
    pass


def delete_internal_user(request):
    # TODO
    pass

