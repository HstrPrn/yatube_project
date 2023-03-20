from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import Post, Group, SHOWN_CHARS_COUNT


User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Test group',
            slug='Test_slug',
            description='Test description'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test post0123456789'
        )

    def test_models_have_correct_object_name(self):
        """Проверяем, что у моделей корректно работает метод __str__."""
        self.assertEqual(str(self.group),
                         self.group.title)
        self.assertEqual(str(self.post),
                         self.post.text[:SHOWN_CHARS_COUNT])
