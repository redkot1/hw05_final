from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

User = get_user_model()


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Заголовок',
            slug='test-slug',
            description='Описание',
        )
        cls.author = User.objects.create_user(username='tester')
        posts = []
        for number in range(13):
            posts.append(Post(
                text='Текст для теста' + str(number),
                group=cls.group,
                author=cls.author,
            ))
        Post.objects.bulk_create(posts)

    def setUp(self):
        self.user = User.objects.create_user(username='MrA')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_containse_ten_records(self):
        """Количество постов на первой странице равно 10."""
        response = self.client.get(reverse('index'))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_containse_three_records(self):
        """На второй странице должно быть три поста."""
        response = self.client.get(reverse('index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)
