import shutil
import tempfile
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.models import Group, Post, User, Follow

User = get_user_model()


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.group = Group.objects.create(
            title='Заголовок',
            slug='test-slug',
            description='Описание',
        )
        cls.group2 = Group.objects.create(
            title='Заголовок2',
            slug='test-slug2',
            description='Описание2',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Текст для теста',
            group=cls.group,
            author=User.objects.create(username='tester'),
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.get(username='tester')
        self.user2 = User.objects.create_user(username='tester2')
        self.user3 = User.objects.create_user(username='tester3')
        self.authorized_client = Client()
        self.authorized_client2 = Client()
        self.authorized_client3 = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client2.force_login(self.user2)
        self.authorized_client3.force_login(self.user3)

    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'index.html': reverse('index'),
            'post_new.html': reverse('post_new'),
            'group.html': (
                reverse('group_posts', kwargs={'slug': self.group.slug})
            ),
        }

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('index'))
        post_object = response.context.get('page')[0]
        post_author_0 = post_object.author
        post_pub_date_0 = post_object.pub_date
        post_text_0 = post_object.text
        post_group_0 = post_object.group
        post_image_0 = post_object.image
        self.assertEqual(post_author_0, PostsPagesTests.post.author)
        self.assertEqual(post_pub_date_0, PostsPagesTests.post.pub_date)
        self.assertEqual(post_text_0, PostsPagesTests.post.text)
        self.assertEqual(post_group_0, PostsPagesTests.post.group)
        self.assertEqual(post_image_0, PostsPagesTests.post.image)

    def test_group_posts_pages_show_correct_context(self):
        """Шаблон group_posts сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': self.group.slug})
        )
        post_object = response.context.get('page')[0]
        self.assertEqual(
            response.context['group'].title, self.group.title)
        self.assertEqual(
            response.context['group'].description, self.group.description)
        self.assertEqual(
            response.context['group'].slug, self.group.slug)
        self.assertNotEqual(
            response.context['group'].slug, self.group2.slug)
        post_author_0 = post_object.author
        post_pub_date_0 = post_object.pub_date
        post_text_0 = post_object.text
        post_group_0 = post_object.group
        post_image_0 = post_object.image
        self.assertEqual(post_author_0, PostsPagesTests.post.author)
        self.assertEqual(post_pub_date_0, PostsPagesTests.post.pub_date)
        self.assertEqual(post_text_0, PostsPagesTests.post.text)
        self.assertEqual(post_group_0, PostsPagesTests.post.group)
        self.assertEqual(post_image_0, PostsPagesTests.post.image)

    def test_group_posts_pages_show_noposts(self):
        """Пост не попал в группу, для которой не был предназначен."""
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': self.group2.slug})
        )
        response = response.context.get('page')
        self.assertEqual(0, len(response))

    def test_post_new_page_shows_correct_context(self):
        """Шаблон post_new сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('post_new'))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_new_page_shows_correct_context(self):
        """Шаблон post_new сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('post_edit', kwargs={'username': self.user.username,
                                         'post_id': self.post.id}))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_profile_page_shows_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('profile', kwargs={'username': self.user.username}))
        post_object = response.context.get('page')[0]
        profile_object = response.context.get('profile')
        post_count = response.context.get('post_count')
        post_author_0 = post_object.author
        post_pub_date_0 = post_object.pub_date
        post_text_0 = post_object.text
        post_group_0 = post_object.group
        profile_username = profile_object.username
        post_image_0 = post_object.image
        self.assertEqual(post_author_0, PostsPagesTests.post.author)
        self.assertEqual(post_pub_date_0, PostsPagesTests.post.pub_date)
        self.assertEqual(post_text_0, PostsPagesTests.post.text)
        self.assertEqual(post_group_0, PostsPagesTests.post.group)
        self.assertEqual(profile_username,
                         PostsPagesTests.post.author.username)
        self.assertEqual(post_count, 1)
        self.assertEqual(post_image_0, PostsPagesTests.post.image)

    def test_post_view_page_shows_correct_context(self):
        """Шаблон post сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('post', kwargs={'username': self.user.username,
                                    'post_id': self.post.id}))
        post_object = response.context.get('post')
        profile_object = response.context.get('profile')
        post_count = response.context.get('post_count')
        post_author = post_object.author
        post_pub_date = post_object.pub_date
        post_text = post_object.text
        post_group = post_object.group
        profile_username = profile_object.username
        post_image = post_object.image
        self.assertEqual(post_author, PostsPagesTests.post.author)
        self.assertEqual(post_pub_date, PostsPagesTests.post.pub_date)
        self.assertEqual(post_text, PostsPagesTests.post.text)
        self.assertEqual(post_group, PostsPagesTests.post.group)
        self.assertEqual(profile_username,
                         PostsPagesTests.post.author.username)
        self.assertEqual(post_count, 1)
        self.assertEqual(post_image, PostsPagesTests.post.image)

    def test_index_page_cache(self):
        """Проверка кэша шаблона index."""
        response_1 = self.authorized_client.get(reverse('index'))
        post = Post.objects.create(
            text='Cache Test',
            author=self.user,
        )
        self.assertTrue(
            Post.objects.filter(
                text=post.text
            ).exists()
        )
        response_2 = self.authorized_client.get(reverse('index'))
        self.assertEqual(response_1.content, response_2.content)

    def test_follow_user(self):
        """Проверка системы подписок."""
        self.authorized_client.get(
            reverse('profile_follow',
                    kwargs={'username': self.user2.username, }))
        follower = Follow.objects.filter(user=self.user).count()
        self.assertEqual(1, follower, 'Не работает подписка!')

    def test_unfollow_user(self):
        """Проверка системы отписок."""
        self.authorized_client.get(
            reverse('profile_unfollow',
                    kwargs={'username': self.user2.username, }))
        follower = Follow.objects.filter(user=self.user).count()
        self.assertEqual(0, follower, 'Не работает отписка!')

    def test_follow_index_correct_context(self):
        """Проверка новых записей у подписчиков"""
        self.authorized_client2.get(
            reverse('profile_follow',
                    kwargs={'username': self.user.username, }))
        response = self.authorized_client2.get(reverse('follow_index'))
        post_object = response.context.get('page')
        self.assertNotEqual(0, len(post_object), 'Объект должен быть!')
        response_2 = self.authorized_client3.get(reverse('follow_index'))
        post_object_2 = response_2.context.get('page')
        self.assertEqual(0, len(post_object_2), 'Объекта быть не должно!')
