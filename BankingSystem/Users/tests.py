from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.urls import resolve
from . import models
from . import views

# Create your tests here.
class IndividualTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='admin', email='admin@gmail.com', password='adminadmin')
        self.customer = models.Individual.objects.create(user=self.user, phone_number='12345678910', mailing_adress='This is my sample address')

    def test_view_personal_details_success_status_code(self):
        url = reverse('view_personal_details')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_view_personal_details_url_resolves_personal_details_view(self):
        view = resolve('/users/external/getdetails/')
        self.assertEquals(view.func, views.view_personal_details)

    def test_update_personal_details_url_resolves_update_personal_details_view(self):
        view = resolve('/users/external/updatedetails/')
        self.assertEquals(view.func, views.update_personal_details)