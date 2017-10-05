from django.shortcuts import render

# Create your views here.

from twilio.rest import Client
from BankingSystem import settings
# Create your views here.


def sms(request):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    message = client.messages.create(to='xxxxxxxx', from_='xxxxxxx', body='This message is sent through twilio api using django framework by akshat.')

    print(message.sid)

    return render()
