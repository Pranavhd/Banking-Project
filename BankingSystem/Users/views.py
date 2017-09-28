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
#    if not request.user.is_authenticated():
#        return HttpResponse(status=401)
    try:
        customer = models.Individual.objects.get(user=user)
    except models.Individual.DoesNotExist:
        return HttpResponse(status=400)

    # update customer details
    customer.user.username = request.POST['username']
    customer.user.email = request.POST['email']
    customer.mail_address = request.POST['mail_address']
    customer.save()
    return HttpResponse(status=201)
