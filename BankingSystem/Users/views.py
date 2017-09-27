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
#    customer_form = form.UpdatePersonalDetailsForm(request.POST)

#    if not customer_form.is_valid():
 #       return HttpResponse(status=400)

    # check if customer/merchant exists with that username
    try:
        customer = models.Individual.objects.get(user=user)
    except models.Individual.DoesNotExist:
        return HttpResponse(status=400)

    # update customer details
    customer.user.username = request.POST['username'] if request.POST.get('username', None) else customer.user.username
    customer.user.email = request.POST['email'] if request.POST.get('email', None) else customer.user.email
    customer.phone_number = request.POST['phonenumber'] if request.POST.get('phonenumber', None) else customer.phone_number
    customer.mailing_adress = request.POST['mailingaddress'] if request.POST.get('mailingaddress', None) else customer.mailing_adress
    customer.save()
    return HttpResponse(status=201)
