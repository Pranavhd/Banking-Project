from django.shortcuts import render
from django.core.mail import send_mail
#from ProjectSS.Email import Model_name

# Create your views here.
def send_email(request):
    Email_to = ['SoftSecu@yandex.com']
    #Email_to.append(Model_name.objects.raw("Select emailID from table where username={} and password={}"))
    if request.method=='POST':
        send_mail('Subject here', 'Here is the message.', 'SoftSecu@yandex.com', Email_to, fail_silently=False)
    return render(request, 'Email/send_email.html', {})
