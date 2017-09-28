from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from . import models
from . import form

# Create your views here.

# defining view for getting personal details information
def view_personal_details(request):
    user = User.objects.first()  # TODO: get the currently logged in user
    emp = models.Employee.objects.get(user=user)
    return render(request, 'personal_details.html', {'emp': emp})


# defining view for updating personal details information
def update_personal_details(request):
    user = User.objects.first()     # TODO: get the currently logged in user
    try:
        employee = models.Employee.objects.get(user=request.user)
    except models.Employee.DoesNotExist:
        return HttpResponse(status=400)
    # update employee details
    employee.user.username = request.POST['username']
    employee.user.email = request.POST['email']
    employee.mail_address = request.POST['mailing_address']
    employee.save()
    return HttpResponse(status=201)