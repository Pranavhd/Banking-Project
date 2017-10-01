from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from . import models
from .form import UpdatePersonalDetailsForm

# Create your views here.

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
