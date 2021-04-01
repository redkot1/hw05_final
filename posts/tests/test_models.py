from django.test import TestCase

from posts.models import Group, Post, User


class PostsModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title='Заголовок',
            slug='Ссылка',
            description='Описание',
        )
        cls.post = Post.objects.create(
            text='Текст для теста',
            group=cls.group,
            author=User.objects.create(username='Admin'),
        )

    def test_verbose_name(self):
        post = PostsModelTest.post
        field_verboses = {
            'text': 'Текст',
            'group': 'Группа',
            'author': 'Автор',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected
                )

    def test_help_text(self):
        post = PostsModelTest.post
        field_help_texts = {
            'group': 'Группа',
            'text': 'Текст поста'
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected
                )

    def test_str(self):
        post = PostsModelTest.post
        text = post.text
        self.assertEqual(str(post), text[:15])

    def test_group_title(self):
        group = PostsModelTest.group
        title = str(group)
        self.assertEqual(title, group.title)
