from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from posts.models import Post, Group


User = get_user_model()


class PostFormTests(TestCase):
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
            group=cls.group,
        )

    def setUp(self):
        self.guest_user = Client()

        self.user = PostFormTests.author
        self.auth_user = Client()
        self.auth_user.force_login(self.user)

    def test_creating_post_form_by_auth_user(self):
        """
        После отправки валидной формы создается новый пост
        и происходит правильный редирект.
        """
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Test text',
            'group': self.group.id,
        }
        auth_response = self.auth_user.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(auth_response, reverse(
            'posts:profile', kwargs={'username': PostFormTests.author}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=self.group.id
            ).exists()
        )

    def test_creating_post_form_by_guest_user(self):
        """Неавторизованный пользователь не сможет создавать посты."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Test text',
            'group': self.group.id,
        }
        self.guest_user.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertFalse(
            Post.objects.filter(
                text=form_data['text'],
                group=self.group.id
            ).exists()
        )

    def test_editing_post_form_by_auth_user(self):
        """Проверяем изменение выбранного поста после редактирования."""
        posts_count = Post.objects.count()
        group = Group.objects.create(
            title='Edit group',
            slug='edit_slug',
            description='Edit group description'
        )
        form_data = {
            'text': 'Edited text.',
            'group': group.id
        }
        self.auth_user.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group']
            ).exists()
        )

    def test_editing_post_form_by_guest_user(self):
        """Неавторизованный пользователь не сможет отредактировать пост."""
        posts_count = Post.objects.count()
        group = Group.objects.create(
            title='Edit group',
            slug='edit_slug',
            description='Edit group description'
        )
        form_data = {
            'text': 'Edited text.',
            'group': group.id
        }
        self.guest_user.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertFalse(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group']
            ).exists()
        )
