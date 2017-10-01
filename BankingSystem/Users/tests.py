from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.urls import resolve
from . import models
from . import views

# Create your tests here.
class IndividualTestForViewingPersonalDetails(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='admin', email='admin@gmail.com', password='adminadmin')
        customer = models.Individual.objects.create(user=user, phone_number='12345678910', mail_address='This is my sample address')
        url = reverse('view_personal_details')
        self.response = self.client.get(url)

    def test_view_personal_details_success_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_view_personal_details_url_resolves_personal_details_view(self):
        view = resolve('/users/external/getdetails/')
        self.assertEquals(view.func, views.view_personal_details)

    def test_view_personal_details_contains_link_to_update_page(self):
        update_personal_details_url = reverse('update_personal_details')
        self.assertContains(self.response, 'action="{0}"'.format(update_personal_details_url))


class IndividualTestForUpdatingPersonalDetails(TestCase):

    def test_update_personal_details_url_resolves_update_personal_details_view(self):
        view = resolve('/users/external/updatedetails/')
        self.assertEquals(view.func, views.update_personal_details)

    # to test whether personal details of a customer are getting updating successfully
    def test_update_personal_details_of_individual_merchant_success(self):

        user=User.objects.create_user(username='admin', email='admin@gmail.com', password='adminpwd')
        individual = models.Individual.objects.create(user=user, phone_number='12345678910', mail_address='This is my sample address')
        url = reverse('update_personal_details')
        customer_data = {'username': 'customer', 'email': 'customer@gmail.com', 'mail_address' : 'Updated address',
                         'phone_number': '72738434995'}
        response = self.client.post(url, customer_data)
        individual.refresh_from_db()
        user.refresh_from_db()
        self.assertEquals(response.status_code, 201)
        self.assertEqual(individual.mail_address, 'Updated address')
        self.assertEquals(user.email, 'customer@gmail.com')
