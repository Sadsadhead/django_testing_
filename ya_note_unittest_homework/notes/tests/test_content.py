# news/tests/test_content.py
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Хозяин заметки')
        cls.user = User.objects.create(username='Пользователь')
        cls.note_args = {
            'title': 'Тестовая заметка',
            'text': 'Просто текст.',
        }
        cls.note = Note.objects.create(
            **cls.note_args,
            author=cls.author,
            slug='testslug',
        )
        cls.note2 = Note.objects.create(
            **cls.note_args,
            author=cls.user,
            slug='testslug2',
        )
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.list = reverse('notes:list')

    def test_authorized_client_has_his_note_in_context(self):
        self.client.force_login(self.author)
        response = self.client.get(self.list)
        self.assertIn(self.note, response.context['object_list'])
        self.assertNotIn(self.note2, response.context['object_list'])

    def test_authorized_client_has_form(self):
        self.client.force_login(self.author)
        response = self.client.get(reverse('notes:add'))
        self.assertIn('form', response.context)
        response = self.client.get(reverse(
            'notes:edit',
            args=(self.note.slug,))
        )
        self.assertIn('form', response.context)
