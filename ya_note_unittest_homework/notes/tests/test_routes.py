from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword'
        )
        cls.other_user = get_user_model().objects.create_user(
            username='otheruser',
            password='otherpassword'
        )
        cls.notes = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.user
        )

    def test_pages_availability(self):
        urls = [
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        ]
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authenticated_user_or_author_access_notes_pages(self):
        self.client.force_login(self.user)
        urls = [
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('notes:detail', {'slug': self.notes.slug}),
            ('notes:edit', {'slug': self.notes.slug}),
            ('notes:delete', {'slug': self.notes.slug}),
        ]
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, kwargs=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_pages_access_for_non_author_returns_404(self):
        self.client.force_login(self.other_user)
        urls = [
            ('notes:detail', {'slug': self.notes.slug}),
            ('notes:edit', {'slug': self.notes.slug}),
            ('notes:delete', {'slug': self.notes.slug}),
        ]
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, kwargs=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_anonymous_user_redirected_to_login(self):
        urls = [
            ('notes:detail', {'slug': 'test-slug'}),
            ('notes:edit', {'slug': 'test-slug'}),
            ('notes:delete', {'slug': 'test-slug'}),
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
        ]
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertRedirects(
                    response,
                    f'/auth/login/?next={url}'
                )
