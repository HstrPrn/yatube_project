import os
import shutil
import tempfile
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile as suf
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Post, Group, Comment, User


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_user = Client()

        self.user = PostFormTests.author
        self.auth_user = Client()
        self.auth_user.force_login(self.user)
        self.pic = (
             b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'
        )
        self.uploaded = suf(
            name='dickpic.png',
            content=self.pic,
            content_type='image/png'
        )

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(os.path.join(
            TEMP_MEDIA_ROOT, 'posts/'), ignore_errors=True)

    def test_creating_post_form_by_auth_user(self):
        """
        После отправки валидной формы создается новый пост
        и происходит правильный редирект.
        """
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Test text',
            'group': self.group.id,
            'image': self.uploaded,
        }
        auth_response = self.auth_user.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(auth_response, reverse(
            'posts:profile', kwargs={'username': self.author}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group'],
                image='posts/dickpic.png'
            ).exists()
        )

    def test_creating_post_form_by_guest_user(self):
        """Неавторизованный пользователь не сможет создавать посты."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Test text',
            'group': self.group.id,
            'image': self.uploaded,
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
                group=form_data['group'],
                image='posts/dickpic.png'
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
            'group': group.id,
            'image': self.uploaded,
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
                group=form_data['group'],
                image='posts/dickpic.png'
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
            'group': group.id,
            'image': self.uploaded,
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
                group=form_data['group'],
                image='posts/dickpic.png'
            ).exists()
        )


class CommentFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_author = User.objects.create_user(username='post_author')
        cls.comment_author = User.objects.create_user(
            username='comment_author'
        )
        cls.post = Post.objects.create(
            author=cls.post_author,
            text='Test post'
        )
        cls.comment = Comment.objects.create(
            author=cls.comment_author,
            post=cls.post,
            text='Comment text'
        )

    def setUp(self):
        self.guest_user = Client()

        self.auth_user = Client()
        self.auth_user.force_login(self.comment_author)

    def test_creating_comment_form_by_auth_user(self):
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'New comment'
        }
        response = self.auth_user.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}
            ))
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertTrue(Comment.objects.filter(
            text=form_data['text']
        ).exists())

    def test_creating_comment_form_by_guest_user(self):
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'New comment'
        }
        self.guest_user.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comments_count)
        self.assertFalse(Comment.objects.filter(
            text=form_data['text']
        ).exists())
