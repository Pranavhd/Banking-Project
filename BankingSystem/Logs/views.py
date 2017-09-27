from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from BankingSystem.Users import models as users_models
from django.core.serializers import serialize
from . import forms
from . import models

# Create your views here.


def get_system_log(request):
    # check if a valid user
    if not request.user.is_authenticated():
        return HttpResponse(status=401)

    # check if it is an admin user
    try:
        employee = users_models.Employee.objects.get(user=request.user)
    except users_models.Employee.DoesNotExist:
        return HttpResponse(status=401)
    if employee.level != 0:
        return HttpResponse(status=401)

    # check POST data is valid
    f = forms.GetSystemLogForm(request.POST)
    if not f.is_valid():
        return HttpResponse(status=400)

    # return rows
    rows = models.SystemLogModel.objects.all()[:int(request.POST['rows'])]
    data = []
    for row in rows:
        data.append((row.title, row.content))
    return HttpResponse(str(data))
