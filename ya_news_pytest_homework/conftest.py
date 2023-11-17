import pytest
from news.models import News
from django.contrib.auth.models import User
from news.models import News


@pytest.fixture
def authenticated_user():
    user = User.objects.create_user(
        username='testuser',
        password='testpassword'
    )
    return user


@pytest.fixture
def create_news_instance():
    return News.objects.create(text='Test content')


@pytest.fixture
def news(author):
    news = News.objects.create(
        title='Заголовок',
        text='Текст заметки'
    )
    return news


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def form_data():
    form_data = {'text': 'Test_text'}
    return form_data
