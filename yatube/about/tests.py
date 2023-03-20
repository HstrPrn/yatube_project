from http import HTTPStatus
from django.test import TestCase, Client


urls = [
    '/about/author/',
    '/about/tech/'
]
code_statuses = [HTTPStatus.OK] * 2
templates = [
    'about/author.html',
    'about/tech.html',
]


class AboutUrlsTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_urls_status_code(self):
        """"""
        for url, status in dict(zip(urls, code_statuses)).items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, status)

    def test_urls_uses_correct_templates(self):
        """"""
        for url, template in dict(zip(urls, templates)).items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertTemplateUsed(response, template)
