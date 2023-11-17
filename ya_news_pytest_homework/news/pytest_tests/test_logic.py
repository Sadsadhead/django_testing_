import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cannot_comment(client, create_news_instance):
    url = reverse('news:detail', args=[create_news_instance.pk])
    response = client.post(url, {'text': 'This is a comment'})
    assert response.status_code == 302
    assert 'login' in response.url
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_authenticated_user_can_comment(
    client,
    authenticated_user,
    create_news_instance
):
    client.force_login(authenticated_user)
    url = reverse('news:detail', args=[create_news_instance.pk])
    response = client.post(url, {'text': 'This is a comment'})
    assert response.status_code == 302
    assert Comment.objects.filter(text='This is a comment').exists()


@pytest.mark.parametrize('word', BAD_WORDS)
def test_user_cant_use_bad_words(author_client, news, word):
    expected_count = Comment.objects.count()
    bad_words_data = {'text': f'Какой-то текст, {word}, еще текст'}
    response = author_client.post(
        reverse(
            'news:detail',
            args=(news.pk,)
        ),
        data=bad_words_data
    )
    comments_count = Comment.objects.count()
    assertFormError(response, form='form', field='text', errors=WARNING)
    assert expected_count == comments_count
