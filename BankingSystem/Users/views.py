from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from . import models
from . import form

# Create your views here.

# defining view for getting personal details information
def view_personal_details(request):
    user = User.objects.first()  # TODO: get the currently logged in user
    individual = models.Individual.objects.get(user=user)
    return render(request, 'personal_details.html', {'customer': individual})


# defining view for updating personal details information
def update_personal_details(request):
    user = User.objects.first()  # TODO: get the currently logged in user
    customer_form = form.UpdatePersonalDetailsForm(request.POST)

    if not customer_form.is_valid():
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
