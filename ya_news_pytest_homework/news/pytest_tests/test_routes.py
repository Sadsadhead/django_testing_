from datetime import date, timedelta

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from news.forms import CommentForm
from news.models import Comment, News

pytestmark = pytest.mark.django_db

PK = 1
COUNT_TEST_NEWS = 15
COUNT_TEST_COMMENT = 15


@pytest.fixture
def news_list():
    return [
        News.objects.create(
            title=f'Новость {i} из {COUNT_TEST_NEWS}'
        ) for i in range(
            1, COUNT_TEST_NEWS
        )
    ]


@pytest.fixture
def comments_list(author, news):
    for i in range(COUNT_TEST_COMMENT):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Комментарий {i} из {COUNT_TEST_COMMENT}',
        )
        comment.created = timezone.now() + timedelta(i)
        comment.save()
    return comments_list


def test_news_count_order(client, news_list):
    response = client.get(reverse('news:home'))
    object_list = list(response.context['object_list'])
    assert len(object_list) == settings.NEWS_COUNT_ON_HOME_PAGE
    assert isinstance(object_list[0].date, date)
    assert object_list == sorted(
        object_list,
        key=lambda x: x.date,
        reverse=True
    )


def test_comments_order(client, news, comments_list):
    response = client.get(reverse('news:detail', args=[news.pk]))
    assert 'news' in response.context
    news = response.context['news']
    comments = list(news.comment_set.all())
    assert isinstance(comments[0].created, timezone.datetime)
    assert comments == sorted(comments, key=lambda x: x.created)


def test_client_has_form(client, admin_client, news):
    detail_url = reverse('news:detail', args=[news.pk])
    response = client.get(detail_url)
    admin_response = admin_client.get(detail_url)
    assert (
        'form' not in response.context
        and isinstance(admin_response.context['form'], CommentForm)
    )
