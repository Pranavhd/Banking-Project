from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.contrib.auth.models import User
from . import models
from django.contrib.sessions.models import Session
import time



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
        # login as t1
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

    def test_admin_update_internal_user_succeed(self):
        # login as admin
        self.client.post('/login/', {'username': 'admin', 'password': 'adminadmin'})
        # update t1 user email
        data = {'username': 't1', 'email': 't1t1@gmail.com'}
        response = self.client.post('/users/internal/update/', data, follow=True)
        self.assertEquals(response.status_code, 201)
        user = User.objects.get(username='t1')
        self.assertEqual(user.email, 't1t1@gmail.com')

    def test_admin_update_internal_user_with_invalid_post_data_failed(self):
        # login as admin
        self.client.post('/login/', {'username': 'admin', 'password': 'adminadmin'})
        # length of 'email' < 100
        data = {'username': 't1', 'email': 't1'*100 + '@gmail.com'}
        response = self.client.post('/users/internal/update/', data, follow=True)
        self.assertEquals(response.status_code, 400)

    def test_t1_or_t2_update_internal_user_failed(self):
        # login as admin
        self.client.post('/login/', {'username': 't1', 'password': 't1t1'})
        # update t1 user
        data = {'username': 't2', 'email': 't2t2@gmail.com'}
        response = self.client.post('/users/internal/update/', data, follow=True)
        self.assertEquals(response.status_code, 401)

    def test_admin_delete_internal_user_succeed(self):
        # login as admin
        self.client.post('/login/', {'username': 'admin', 'password': 'adminadmin'})
        # delete t2 user
        data = {'username': 't2'}
        response = self.client.post('/users/internal/delete/', data, follow=True)
        self.assertEquals(response.status_code, 201)
        with self.assertRaises(User.DoesNotExist):
            _ = User.objects.get(username='t2')

    def test_t1_or_t2_delete_internal_user_failed(self):
        # login as t1
        self.client.post('/login/', {'username': 't1', 'password': 't1t1'})
        # delete t2 user
        data = {'username': 't2'}
        response = self.client.post('/users/internal/delete/', data, follow=True)
        self.assertEquals(response.status_code, 401)

    # test case for 300 sec is not practical
    def test_admin_session_not_timeout(self):
        self.client.post('/login/', {'username': 'admin', 'password': 'adminadmin'})
        # update server session for admin user
        a = Session.objects.all()[0]
        # b = a.expire_date
        # print(b)
        data = {'username': 'new', 'email': 'new@gmail.com', 'password': 'newnew', 'level': 0}

        time.sleep(2)

        response = self.client.post('/users/internal/create/', data, follow=True)
        self.assertEquals(response.status_code, 201)

    def test_admin_session_not_timeout(self):
        self.client.post('/login/', {'username': 'admin', 'password': 'adminadmin'})
        # update server session for admin user
        a = Session.objects.all()[0]
        # b = a.expire_date
        # print(b)
        data = {'username': 'new', 'email': 'new@gmail.com', 'password': 'newnew', 'level': 0}

        time.sleep(5)

        response = self.client.post('/users/internal/create/', data, follow=True)
        self.assertEquals(response.status_code, 201)

    def test_admin_session_timeout(self):
        self.client.post('/login/', {'username': 'admin', 'password': 'adminadmin'})
        # update server session for admin user
        a = Session.objects.all()[0]
        # b = a.expire_date
        # print(b)
        data = {'username': 'new', 'email': 'new@gmail.com', 'password': 'newnew', 'level': 0}

        time.sleep(11)

        response = self.client.post('/users/internal/create/', data, follow=True)
        self.assertEquals(response.status_code, 401)
