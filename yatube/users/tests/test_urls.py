# from http import HTTPStatus
from django.test import TestCase, Client
from django.contrib.auth import get_user_model


User = get_user_model()


class UsersUrlsTests(TestCase):
    def setUp(self):
        self.user = Client()
