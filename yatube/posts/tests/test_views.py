from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django import forms
from posts.models import Post, Group
from posts.views import SHOWN_POSTS_NUMBER, SHOWN_TITLE_CHAR_COUNT

User = get_user_model()

INDEX: str = 'posts:index'
POST_CREATE: str = 'posts:post_create'
GROUP_LIST: str = 'posts:group_list'
PROFILE: str = 'posts:profile'
POST_DETAIL: str = 'posts:post_detail'
POST_EDIT: str = 'posts:post_edit'

END_PAGE_POSTS_COUNT: int = 3


class PostViewsTests(TestCase):

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
            text='Test post',
            group=cls.group
        )

    def setUp(self):
        self.guest_user = Client()

        self.user = PostViewsTests.author
        self.auth_user = Client()
        self.auth_user.force_login(self.user)

    def test_views_uses_correct_template_with_auth_user(self):
        """
        URL-адреса использую соответствующий шаблон для
        зарегистрированного пользователя.
        """
        views_templates = {
            reverse(INDEX): 'posts/index.html',
            reverse(POST_CREATE): 'posts/create_post.html',
            reverse(
                GROUP_LIST,
                kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                PROFILE,
                kwargs={'username': self.author}
            ): 'posts/profile.html',
            reverse(
                POST_DETAIL,
                kwargs={'post_id': self.post.id}
            ): 'posts/post_detail.html',
            reverse(
                POST_EDIT,
                kwargs={'post_id': self.post.id}
            ): 'posts/create_post.html',
        }
        for view, template in views_templates.items():
            auth_response = self.auth_user.get(view)
            with self.subTest(view=view):
                self.assertTemplateUsed(auth_response, template)

    def test_views_uses_correct_template_with_guest_user(self):
        """
        URL-адреса использую соответствующий шаблон для
        незарегистрированного пользователя.
        """
        used_templates = {
            reverse(INDEX): 'posts/index.html',
            reverse(
                GROUP_LIST,
                kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                PROFILE,
                kwargs={'username': self.author}
            ): 'posts/profile.html',
            reverse(
                POST_DETAIL,
                kwargs={'post_id': self.post.id}
            ): 'posts/post_detail.html',
        }
        unused_templates = {
            reverse(POST_CREATE): 'posts/create_post.html',
            reverse(
                POST_EDIT,
                kwargs={'post_id': self.post.id}
            ): 'posts/create_post.html',
        }
        for view, template in used_templates.items():
            guest_response = self.guest_user.get(view)
            with self.subTest(view=view):
                self.assertTemplateUsed(guest_response, template)

        for view, template in unused_templates.items():
            guest_response = self.guest_user.get(view)
            with self.subTest(view=view):
                self.assertTemplateNotUsed(guest_response, template)

    def test_index_page_show_correct_context(self):
        """Главная страница возвращает ожидаемый контекст."""
        response = self.auth_user.get(reverse(INDEX))
        self.assertEqual(response.context['page_obj'][0], self.post)

    def test_profile_page_show_correct_context(self):
        """Страница профиля возвращает ожидаемый контекст."""
        response = self.auth_user.get(
            reverse(PROFILE,
                    kwargs={'username': self.author})
        )
        self.assertEqual(response.context['page_obj'][0], self.post)
        self.assertEqual(response.context['username'], self.author)
        self.assertEqual(response.context['total_posts'],
                         Post.objects.all().count())

    def test_group_list_page_show_correct_context(self):
        """Страница группы возвращает ожидаемый контекст."""
        response = self.auth_user.get(
            reverse(GROUP_LIST,
                    kwargs={'slug': self.group.slug})
        )
        self.assertEqual(response.context['page_obj'][0], self.post)
        self.assertEqual(response.context['group'], self.group)

    def test_post_detail_page_show_correct_context(self):
        """Страница поста возвращает ожидаемый контекст."""
        response = self.auth_user.get(
            reverse(POST_DETAIL,
                    kwargs={'post_id': self.post.id})
        )
        self.assertEqual(response.context['posts_count'],
                         Post.objects.all().count())
        self.assertEqual(response.context['post'], self.post)
        self.assertEqual(response.context['title'],
                         self.post.text[:SHOWN_TITLE_CHAR_COUNT])

    def test_create_and_edit_post_pages_show_correct_contest(self):
        """
        Страницы создания и редактирования поста
        возвращает ожидаемый контекст.
        """
        views = [
            self.auth_user.get(reverse(POST_CREATE)),
            self.auth_user.get(reverse(POST_EDIT,
                               kwargs={'post_id': self.post.id})),
        ]
        for response in views:
            form_field = {
                'text': forms.fields.CharField,
                'group': forms.models.ModelChoiceField,
            }
            for value, expected in form_field.items():
                with self.subTest(value=value):
                    field = response.context['form'].fields[value]
                    self.assertIsInstance(field, expected)

    def test_post_creating_with_group(self):
        """
        Пост после создания виден на главной странице,
        странице группы этого поста и странице профиле.
        Пост не виден на странице группы, к которой он не относится.
        """
        views = [
            reverse(INDEX),
            reverse(GROUP_LIST,
                    kwargs={'slug': self.group.slug}),
            reverse(PROFILE,
                    kwargs={'username': self.author}),
        ]
        posts_count = Post.objects.count()
        Group.objects.create(
            title='Temp group',
            slug='temp_slug',
            description='Temp discription',
        )
        form_data = {
            'text': 'Test text',
            'group': self.group.id
        }
        self.auth_user.post(reverse(POST_CREATE), data=form_data)
        for view in views:
            with self.subTest(view=view):
                new_posts_count = len(
                    self.auth_user.get(view).context['page_obj']
                )
                self.assertEqual(new_posts_count, posts_count + 1)
        test_group_posts_count = len(
            self.auth_user.get(
                reverse(GROUP_LIST,
                        kwargs={'slug': 'temp_slug'})
            ).context['page_obj']
        )
        self.assertNotEqual(test_group_posts_count, posts_count + 1)


class PaginatorTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Test group',
            slug='test_slug',
            description='Test description'
        )
        Post.objects.bulk_create([
            Post(
                author=cls.author,
                text=f'Test post #{i}',
                group=cls.group
            ) for i in range(13)
        ])

    def setUp(self):
        self.auth_user = Client()
        self.user = User.objects.create_user(username='auth')
        self.auth_user.force_login(self.author)
        self.views = [
            reverse(INDEX),
            reverse(GROUP_LIST,
                    kwargs={'slug': self.group.slug}),
            reverse(PROFILE,
                    kwargs={'username': self.author}),
        ]

    def test_first_page_contains_ten_records(self):
        """На первой странице отображается 10 постов"""
        for view in self.views:
            with self.subTest(view=view):
                response = self.auth_user.get(view)
                self.assertEqual(len(response.context['page_obj']),
                                 SHOWN_POSTS_NUMBER)

    def test_index_last_page_contains_two_records(self):
        """На последней странице отображается 3 поста"""
        for view in self.views:
            with self.subTest(view=view):
                response = self.auth_user.get(view + '?page=2')
                self.assertEqual(len(response.context['page_obj']),
                                 END_PAGE_POSTS_COUNT)
