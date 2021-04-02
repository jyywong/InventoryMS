from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model
from inventory.views import *

class CreateLabTests(TestCase):
    def test_create_lab_login_required(self):
        self.url = reverse('create_lab')
        login_url = reverse('login')
        response = self.client.get(self.url)
        self.assertRedirects(response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))

class CreateLabTestsLoggedIn(TestCase):
    def setUp(self):
        self.username = 'jon'
        self.password = '1234'
        self.user = get_user_model().objects.create(
            username = self.username,
            password = self.password
        )
        self.client.force_login(self.user)
        self.url = reverse('create_lab')
        self.response = self.client.get(self.url)
    def test_create_lab_status_code(self):
        self.assertEqual(self.response.status_code, 200)
    def test_create_lab_contains_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')
    def test_create_lab_resolves_create_lab_view(self):
        view = resolve('/create_lab')
        self.assertEqual(view.func.view_class, Lab_Create)
    def test_new_lab_created(self):
        self.response = self.client.post(self.url,{
            'name' : 'Test Name'
        })
        self.assertEqual(Lab.objects.count(), 1)

class LabListLoggedOut(TestCase):
    def test_lab_list_login_required(self):
        self.url = reverse('lab_list')
        login_url = reverse('login')
        response = self.client.get(self.url)
        self.assertRedirects(response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))

class LabListLoggedIn(TestCase):
    def setUp(self):
        self.username = 'jon'
        self.password = '1234'
        self.user = get_user_model().objects.create(
            username = self.username,
            password = self.password
        )
        self.client.force_login(self.user)
        self.url = reverse('lab_list')
        self.response = self.client.get(self.url)
    def test_lab_list_status_code(self):
        self.assertEqual(self.response.status_code, 200)
    def test_lab_list_resolves_lab_list_view(self):
        view = resolve('/my_labs')
        self.assertEqual(view.func.view_class, LabList)

class LabViewLoggedOut(TestCase):
    def test_lab_view_login_required(self):
        self.url = reverse('lab_view', kwargs={'pk': 1})
        login_url = reverse('login')
        response = self.client.get(self.url)
        self.assertRedirects(response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))

class LabViewLoggedIn(TestCase):
    def setUp(self):
        self.username = 'jon'
        self.password = '1234'
        self.user = get_user_model().objects.create(
            username = self.username,
            password = self.password
        )
        self.lab = Lab.objects.create(
            name = 'Test Lab'
        )
        self.client.force_login(self.user)
        self.url = reverse('lab_view', kwargs={'pk': self.lab.id})
        self.response = self.client.get(self.url)
    def test_lab_view_no_permission_status_code(self):
        self.assertEqual(self.response.status_code, 403)
    def test_lab_view_successful_status_code(self):
        self.lab.members.add(self.user)
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)

'''
Lab add is obsolete
'''

class InviteMemberLoggedOut(TestCase):
    def test_invite_member_login_required(self):
        self.url = reverse('invite_member', kwargs={'pk': 1})
        login_url = reverse('login')
        response = self.client.get(self.url)
        self.assertRedirects(response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))

class InviteMemberLoggedIn(TestCase):
    def setUp(self):
        self.username = 'jon'
        self.password = '1234'
        self.user = get_user_model().objects.create(
            username = self.username,
            password = self.password
        )
        self.lab = Lab.objects.create(
            name = 'Test Lab'
        )
        self.client.force_login(self.user)
        self.url = reverse('invite_member', kwargs={'pk': self.lab.id})
        self.response = self.client.get(self.url)
    def test_lab_view_no_permission_status_code(self):
        self.assertEqual(self.response.status_code, 403)
    def test_lab_view_successful_status_code(self):
        self.lab.members.add(self.user)
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)