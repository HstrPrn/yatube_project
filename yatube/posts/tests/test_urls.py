from http import HTTPStatus
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from posts.models import Post, Group


User = get_user_model()


class PostUrlsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Test group',
            slug='test_slug',
            description='Test description',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Test post0123456789',
        )

    def setUp(self):
        self.guest_user = Client()

        self.user = PostUrlsTests.author
        self.auth_user = Client()
        self.auth_user.force_login(self.user)

    def test_pages_status_code_for_guest_user(self):
        """
        Проверяем статус запрашиваемых страниц для
        незарегистрированного пользователя.
        """
        urls_status = {
            '/': HTTPStatus.OK,
            '/create/': HTTPStatus.FOUND,
            f'/group/{self.group.slug}/': HTTPStatus.OK,
            f'/profile/{self.author}/': HTTPStatus.OK,
            f'/posts/{self.post.id}/': HTTPStatus.OK,
            f'/posts/{self.post.id}/edit/': HTTPStatus.FOUND,
            'unexpected_page': HTTPStatus.NOT_FOUND,
        }
        for url, http_status in urls_status.items():
            with self.subTest(url=url):
                response = self.guest_user.get(url)
                self.assertEqual(response.status_code, http_status)

    def test_pages_status_code_for_auth_user(self):
        """
        Проверяем статус запрашиваемых страниц для
        зарегистрированного пользователя.
        """
        urls_status = {
            '/': HTTPStatus.OK,
            '/create/': HTTPStatus.OK,
            f'/group/{self.group.slug}/': HTTPStatus.OK,
            f'/profile/{self.author}/': HTTPStatus.OK,
            f'/posts/{self.post.id}/': HTTPStatus.OK,
            f'/posts/{self.post.id}/edit/': HTTPStatus.OK,
            'unexpected_page': HTTPStatus.NOT_FOUND,
        }
        for url, http_status in urls_status.items():
            with self.subTest(url=url):
                response = self.auth_user.get(url)
                self.assertEqual(response.status_code, http_status)

    def test_urls_uses_correct_template(self):
        """URL-адреса использую соответствующий шаблон."""
        urls_templates = {
            '/': 'posts/index.html',
            '/create/': 'posts/create_post.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.author}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
        }
        for url, template in urls_templates.items():
            with self.subTest(url=url):
                response = self.auth_user.get(url)
                self.assertTemplateUsed(response, template)

    def test_redirect_guest_user(self):
        """Редирект неавторизованного пользователя на страницу логина."""
        urls_redirect = {
            '/create/': '/auth/login/',
            f'/posts/{self.post.id}/edit/': '/auth/login/',
        }
        for url, redirect in urls_redirect.items():
            with self.subTest(url=url):
                response = self.guest_user.get(url, follow=True)
                self.assertRedirects(response, f'{redirect}?next={url}')
