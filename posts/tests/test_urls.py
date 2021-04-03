from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from http import HTTPStatus

from posts.models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Заголовок',
            slug='test-slug',
            description='Описание',
        )
        cls.post = Post.objects.create(
            text='Текст для теста',
            group=cls.group,
            author=User.objects.create(username='redkot'),
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        self.user2 = User.objects.create_user(username='MrAnderson')
        # помещаем в переменную автора нашего тестового поста
        self.user = User.objects.get(username='redkot')
        # Создаем второй и третий клиент
        self.authorized_client = Client()
        self.authorized_client2 = Client()
        # Авторизуем пользователей
        self.authorized_client.force_login(self.user)
        self.authorized_client2.force_login(self.user2)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'index.html',
            '/new/': 'post_new.html',
            f'/group/{self.group.slug}/': 'group.html',
            f'/{self.user.username}/': 'profile.html',
            f'/{self.user.username}/{self.post.id}/': 'post.html',
            f'/{self.user.username}/{self.post.id}/edit/': 'post_new.html',
        }
        for reverse_name, template in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_guest_response_private(self):
        """Проверка редиректа неавторизованного клиента"""
        templates_url_names_private = {
            '/new/': 'post_new.html',
            f'/{self.user.username}/{self.post.id}/edit/': 'post_new.html',
        }
        for reverse_name, template in templates_url_names_private.items():
            with self.subTest():
                response = self.guest_client.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_guest_response_public(self):
        """Проверка доступа неавторизованного клиента"""
        templates_url_names_public = {
            '/': 'index.html',
            f'/group/{self.group.slug}/': 'group.html',
            f'/{self.user.username}/': 'profile.html',
            f'/{self.user.username}/{self.post.id}/': 'post.html',
        }
        for reverse_name, template in templates_url_names_public.items():
            with self.subTest():
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_noauthor_response_edit(self):
        """Редактирование поста авторизованным клиентом(не автором)"""
        response = self.authorized_client2.get(
            f'/{self.user.username}/{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_404_response(self):
        """Проверка на получение 404 при неверном адресе"""
        response = self.guest_client.get('/missing/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_guest_response_comment(self):
        """Доступ комментирования поста неавторизованным клиентом"""
        response = self.guest_client.get(
            f'/{self.user.username}/{self.post.id}/comment/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
