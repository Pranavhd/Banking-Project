from django.test import TestCase
from django.contrib.auth.models import User
from . import models


class EmployeeTest(TestCase):
    def setUp(self):
        # admin
        user = User.objects.create_user(username='admin', email='admin@gmail.com', password='adminadmin')
        models.Employee.objects.create(user=user, level=0)
        # t1
        user = User.objects.create_user(username='t1', email='t1@gmail.com', password='t1t1')
        models.Employee.objects.create(user=user, level=1)
        # t2
        user = User.objects.create_user(username='t2', email='t2@gmail.com', password='t2t2')
        models.Employee.objects.create(user=user, level=2)

    def test_admin_create_internal_user_succeed(self):
        # login as admin
        self.client.post('/login/', {'username': 'admin', 'password': 'adminadmin'})
        # create admin user
        data = {'username': 'new', 'email': 'new@gmail.com', 'password': 'newnew', 'level': 0}
        response = self.client.post('/users/internal/create/', data, follow=True)
        self.assertEquals(response.status_code, 201)
        # create t1 user
        data = {'username': 'new1', 'email': 'new@gmail.com', 'password': 'newnew', 'level': 1}
        response = self.client.post('/users/internal/create/', data, follow=True)
        self.assertEquals(response.status_code, 201)
        # create t2 user
        data = {'username': 'new2', 'email': 'new@gmail.com', 'password': 'newnew', 'level': 2}
        response = self.client.post('/users/internal/create/', data, follow=True)
        self.assertEquals(response.status_code, 201)

    def test_admin_create_internal_duplicate_username_failed(self):
        # login as admin
        self.client.post('/login/', {'username': 'admin', 'password': 'adminadmin'})
        # create admin user
        data = {'username': 'new', 'email': 'new@gmail.com', 'password': 'newnew', 'level': 0}
        response = self.client.post('/users/internal/create/', data, follow=True)
        self.assertEquals(response.status_code, 201)
        # create t1 user
        data = {'username': 'new', 'email': 'new@gmail.com', 'password': 'newnew', 'level': 1}
        response = self.client.post('/users/internal/create/', data, follow=True)
        self.assertEquals(response.status_code, 400)

    def test_admin_create_internal_user_with_invalid_post_data_failed(self):
        # login as admin
        self.client.post('/login/', {'username': 'admin', 'password': 'adminadmin'})
        # 'level' must in [0, 1, 2]
        data = {'username': 'new', 'email': 'new@gmail.com', 'password': 'newnew', 'level': 4}
        response = self.client.post('/users/internal/create/', data, follow=True)
        self.assertEquals(response.status_code, 400)
        # length of 'username' < 100
        data = {'username': 'new'*100, 'email': 'new@gmail.com', 'password': 'newnew', 'level': 1}
        response = self.client.post('/users/internal/create/', data, follow=True)
        self.assertEquals(response.status_code, 400)

    def test_t1_or_t2_create_internal_user_failed(self):
        # login as admin
        self.client.post('/login/', {'username': 't1', 'password': 't1t1'})
        # create admin user
        data = {'username': 'new', 'email': 'new@gmail.com', 'password': 'newnew', 'level': 0}
        response = self.client.post('/users/internal/create/', data, follow=True)
        self.assertEquals(response.status_code, 401)
        # create t1 user
        data = {'username': 'new1', 'email': 'new@gmail.com', 'password': 'newnew', 'level': 1}
        response = self.client.post('/users/internal/create/', data, follow=True)
        self.assertEquals(response.status_code, 401)
        # create t2 user
        data = {'username': 'new2', 'email': 'new@gmail.com', 'password': 'newnew', 'level': 2}
        response = self.client.post('/users/internal/create/', data, follow=True)
        self.assertEquals(response.status_code, 401)


