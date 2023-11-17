# news/tests/test_content.py
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    TITLE_NOTE = 'Тестовая заметка'
    TEXT_NOTE = 'Текст заметки'
    SLUG_NOTE = 'testslug'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Хозяин заметки')
        cls.user = User.objects.create(username='Пользователь')
        cls.form_data = {
            'title': cls.TITLE_NOTE,
            'text': cls.TEXT_NOTE,
        }
        cls.note = Note.objects.create(
            **cls.form_data,
            author=cls.author,
            slug=cls.SLUG_NOTE,
        )

    def test_auto_generate_slug_if_not_filled(self):
        note = Note.objects.create(
            author=self.author,
            **self.form_data,
        )
        expected_slug = slugify(note.title)
        self.assertEqual(note.slug, expected_slug)

    def test_cannot_create_notes_with_same_slug(self):
        duplicate_slug_note = Note(
            **self.form_data,
            author=self.user,
            slug='testslug',
        )
        with self.assertRaises(Exception):
            duplicate_slug_note.save()

    def test_anonymous_user_cant_create_comment(self):
        notes_count = Note.objects.count()
        self.client.post(reverse('notes:add'), data=self.form_data)
        self.assertEqual(Note.objects.count(), notes_count)

    def test_user_can_delete_own_note(self):
        self.client.force_login(self.author)
        delete_url = reverse('notes:delete', args=[self.note.slug])
        response = self.client.get(delete_url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 302)
        with self.assertRaises(Note.DoesNotExist):
            Note.objects.get(slug=self.note.slug)

    def test_user_cannot_delete_other_user_note(self):
        self.client.force_login(self.user)
        delete_url = reverse('notes:delete', args=[self.note.slug])
        response = self.client.get(delete_url)
        self.assertEqual(response.status_code, 404)
        delete_url = reverse('notes:edit', args=[self.note.slug])
        response = self.client.get(delete_url)
        self.assertEqual(response.status_code, 404)
