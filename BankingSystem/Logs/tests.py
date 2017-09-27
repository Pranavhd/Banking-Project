from django.test import TestCase
from . import models
from BankingSystem.Users import models as users_models

# Create your tests here.


class AdminLogsTest(TestCase):
    def setUp(self):
        # admin
        user = users_models.User.objects.create_user(username='admin', email='admin@gmail.com', password='adminadmin')
        users_models.Employee.objects.create(user=user, level=0)
        # t1
        user = users_models.User.objects.create_user(username='t1', email='t1@gmail.com', password='t1t1')
        users_models.Employee.objects.create(user=user, level=1)
        # logs
        models.SystemLogModel.objects.create(title='a', content='aa')
        models.SystemLogModel.objects.create(title='b', content='bb')
        models.SystemLogModel.objects.create(title='c', content='cc')
        models.SystemLogModel.objects.create(title='d', content='dd')
        models.SystemLogModel.objects.create(title='e', content='ee')
        models.SystemLogModel.objects.create(title='f', content='ff')

    def test_admin_get_system_log_succeed(self):
        # login as admin
        self.client.post('/login/', {'username': 'admin', 'password': 'adminadmin'})
        # get 5 rows
        data = {'rows': 5}
        response = self.client.post('/logs/log/system/', data, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_t1_get_system_log_failed(self):
        # login as t1
        self.client.post('/login/', {'username': 't1', 'password': 't1t1'})
        # get 5 rows
        data = {'rows': 5}
        response = self.client.post('/logs/log/system/', data, follow=True)
        self.assertEquals(response.status_code, 401)
