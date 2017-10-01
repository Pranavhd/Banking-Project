from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from . import models
from .form import UpdatePersonalDetailsForm

# Create your views here.

# defining view for getting personal details information
def view_personal_details(request):
    user = User.objects.first()  # TODO: get the currently logged in user
    employee = models.Employee.objects.get(user=user)
    return render(request, 'personal_details.html', {'emp': employee})


# defining view for updating personal details information
def update_personal_details(request):
    user = User.objects.first()     # TODO: get the currently logged in user
    try:
        employee = models.Employee.objects.get(user=user)
        emp_id = employee.id
    except models.Employee.DoesNotExist:
        return HttpResponse(status=400)
    # update employee details
    if request.method == "POST":
        form = UpdatePersonalDetailsForm(data=request.POST)
        if not form.is_valid():
            return HttpResponse(status=400)

        if form.is_valid():
            user.email = form.cleaned_data['email']
            user.username = form.cleaned_data['username']
            employee.mail_address = form.cleaned_data['mail_address']
            user.save()
            employee.save()
    return HttpResponse(status=201)