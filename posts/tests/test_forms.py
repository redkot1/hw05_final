import os
import shutil
# import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse


from posts.forms import PostForm
from posts.models import Group, Post, User


@override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR, 'temp_img'))
class PostsCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title='Заголовок',
            slug='test-slug',
            description='Описание',
        )
        cls.post = Post.objects.create(
            text='Текст для теста',
            group=PostsCreateFormTests.group,
            author=User.objects.create(username='tester'),
            image=cls.uploaded
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.get(username='tester')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Posts."""
        uploaded2 = SimpleUploadedFile(
            name='small2.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        posts_count = Post.objects.count()
        form_data = {
            'group': PostsCreateFormTests.group.id,
            'text': 'Тестовый текст',
            'image': uploaded2,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('post_new'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse('index'))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Проверяем, что создалась запись с нашим слагом
        self.assertTrue(
            Post.objects.filter(
                group=form_data['group'],
                text=form_data['text'],
                image='posts/small2.gif',
            ).exists()
        )

    def test_edit_post(self):
        """Валидная форма редактирует запись в Posts."""
        posts_count = Post.objects.count()
        form_data = {
            'group': PostsCreateFormTests.group.id,
            'text': 'Отредактированный текст',
        }
        response = self.authorized_client.post(reverse(
            'post_edit',
            kwargs={'username': self.user.username, 'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'post',
            kwargs={'username': self.user.username, 'post_id': self.post.id}))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                group=PostsCreateFormTests.group.id,
                text=form_data['text']
            ).exists()
        )
