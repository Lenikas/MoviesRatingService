import pytest
from flask import json
from movies.app import FILM_STORAGE, USER_STORAGE, find_film, find_user, server
from movies.film import Film
from movies.user import User


@pytest.fixture()
def clear_storage():
    FILM_STORAGE.clear()
    USER_STORAGE.clear()


@pytest.fixture()
def client():
    with server.test_client() as client:
        yield client


@pytest.fixture()
def user():
    exist_user = User('name', 'qwerty', {})
    not_exist_user = User('NAME', 'qwerty', {})
    yield exist_user, not_exist_user


@pytest.fixture()
def user_storage():
    user_storage = [User('name', 'qwerty', {})]
    yield user_storage
    user_storage.clear()


@pytest.fixture()
def film_storage():
    film_storage = [Film('film', 2000, [], [])]
    yield film_storage
    film_storage.clear()


@pytest.fixture()
def film():
    exist_film = Film('film', 2000, [], [])
    not_exist_film = Film('FILM', 2000, [], [])
    yield exist_film, not_exist_film


def test_find_exist_user(user, user_storage):
    with pytest.raises(ValueError):
        find_user(user[1].name, user_storage)


def test_find_user(user, user_storage):
    actual = find_user(user[0].name, user_storage)
    assert isinstance(actual, User)


def test_find_exist_film(film, film_storage):
    with pytest.raises(ValueError):
        find_film(film[1].name, film[1].year, film_storage)


def test_find_film(film, film_storage):
    actual = find_film(film[0].name, film[0].year, film_storage)
    assert isinstance(actual, Film)


def test_add_user(client, clear_storage):
    response = client.post(
        '/movies/api/v1.0/create_account',
        data=json.dumps({'username': 'abc', 'password': 'qwerty'}),
        content_type='application/json',
    )
    data = json.loads(response.get_data())
    assert response.status_code == 200
    assert data['ACTION'] == {'username': 'abc'}


def test_add_user_invalid_data(client, clear_storage):
    response = client.post(
        '/movies/api/v1.0/create_account',
        data=json.dumps({'username': 'abc'}),
        content_type='application/json',
    )
    data = json.loads(response.get_data())
    assert response.status_code == 400
    assert data['ERROR'] == 'Invalid data, please give username and password'


def test_create_film_invalid_data(client, clear_storage):
    response = client.post(
        '/movies/api/v1.0/abc/add',
        data=json.dumps({'name': 'film'}),
        content_type='application/json',
    )
    data = json.loads(response.get_data())
    assert response.status_code == 400
    assert data['ERROR'] == 'Invalid data, please give name and year of film'


def test_create_film_data(client, clear_storage):
    response = client.post(
        '/movies/api/v1.0/abc/add',
        data=json.dumps({'name': 'film', 'year': 2010}),
        content_type='application/json',
    )
    data = json.loads(response.get_data())
    assert response.status_code == 400
    assert data['ERROR'] == 'User does not exist'


def test_create_film(client, clear_storage):
    test_add_user(client, clear_storage)
    #   так можно делать? тут я,чтобы пользователя заново не добавлять,
    #   вызываю тестовый метод,который как раз тестирует добавление пользователя
    response = client.post(
        '/movies/api/v1.0/abc/add',
        data=json.dumps({'name': 'film', 'year': 2010}),
        content_type='application/json',
    )
    data = json.loads(response.get_data())
    assert response.status_code == 200
    assert data['FILM'] == {'name': 'film', 'year': 2010}


def test_get_films_empty(client, clear_storage):
    data = client.get('/movies/api/v1.0/films')
    assert b'LIST OF FILMS' in data.get_data()


def test_get_films(client, clear_storage):
    test_create_film(client, clear_storage)
    data = client.get('/movies/api/v1.0/films')
    assert r'"name":"film"' in data.get_data(as_text=True)
    assert r'"year":2010' in data.get_data(as_text=True)


def test_add_review_invalid_data(client, clear_storage):
    response = client.post(
        '/movies/api/v1.0/abc/add_review',
        data=json.dumps({'name': 'film', 'year': 2010}),
        content_type='application/json',
    )
    data = json.loads(response.get_data())
    assert response.status_code == 400
    assert (
        data['ERROR']
        == 'Invalid data, please give name and year of film and your review'
    )


def test_add_review_not_exist_user(client, clear_storage):
    response = client.post(
        '/movies/api/v1.0/abc/add_review',
        data=json.dumps({'name': 'film', 'year': 2010, 'review': 'review'}),
        content_type='application/json',
    )
    data = json.loads(response.get_data())
    assert response.status_code == 404
    assert data['ERROR'] == 'User does not exist'


def test_add_review_not_exist_film(client, clear_storage):
    test_add_user(client, clear_storage)
    response = client.post(
        '/movies/api/v1.0/abc/add_review',
        data=json.dumps({'name': 'film', 'year': 2010, 'review': 'review'}),
        content_type='application/json',
    )
    data = json.loads(response.get_data())
    assert response.status_code == 404
    assert data['ERROR'] == 'This film does not exist'


def test_add_review_success(client, clear_storage):
    test_create_film(client, clear_storage)
    response = client.post(
        '/movies/api/v1.0/abc/add_review',
        data=json.dumps({'name': 'film', 'year': 2010, 'review': 'review'}),
        content_type='application/json',
    )
    data = json.loads(response.get_data())
    assert data['ADD_REVIEW'] == {'name': 'film', 'review': 'review'}


def test_add_mark_invalid_data(client, clear_storage):
    response = client.post(
        '/movies/api/v1.0/abc/add_mark',
        data=json.dumps({'name': 'film', 'year': 2010}),
        content_type='application/json',
    )
    data = json.loads(response.get_data())
    assert response.status_code == 400
    assert (
        data['ERROR'] == 'Invalid data, please give name and year of film and your mark'
    )


def test_add_mark_not_exist_user(client, clear_storage):
    response = client.post(
        '/movies/api/v1.0/abc/add_mark',
        data=json.dumps({'name': 'film', 'year': 2010, 'mark': 5}),
        content_type='application/json',
    )
    data = json.loads(response.get_data())
    assert response.status_code == 404
    assert data['ERROR'] == 'User does not exist'


def test_add_mark_not_exist_film(client, clear_storage):
    test_add_user(client, clear_storage)
    response = client.post(
        '/movies/api/v1.0/abc/add_mark',
        data=json.dumps({'name': 'film', 'year': 2010, 'mark': 5}),
        content_type='application/json',
    )
    data = json.loads(response.get_data())
    assert response.status_code == 404
    assert (
        data['ERROR']
        == 'This film does not exist or you mark less 0 or more zero, check it'
    )


def test_add_mark_success(client, clear_storage):
    test_create_film(client, clear_storage)
    response = client.post(
        '/movies/api/v1.0/abc/add_mark',
        data=json.dumps({'name': 'film', 'year': 2010, 'mark': 5}),
        content_type='application/json',
    )
    data = json.loads(response.get_data())
    assert data['ADD_MARK'] == {'name': 'film', 'mark': 5}


def test_get_average_not_exist_film(client, clear_storage):
    data = client.get('/movies/api/v1.0/get_average/abc/2222')
    assert 'ERROR' in data.get_data(as_text=True)


def test_get_average(client, clear_storage):
    test_create_film(client, clear_storage)
    data = client.get('/movies/api/v1.0/get_average/film/2010')
    assert 'AVERAGE' in data.get_data(as_text=True)


def test_get_count_reviews_not_exist_film(client, clear_storage):
    data = client.get('/movies/api/v1.0/get_count_reviews/abc/2222')
    assert 'ERROR' in data.get_data(as_text=True)


def test_get_count_reviews(client, clear_storage):
    test_create_film(client, clear_storage)
    data = client.get('/movies/api/v1.0/get_count_reviews/film/2010')
    assert 'COUNT_REVIEWS' in data.get_data(as_text=True)


def test_get_count_marks_not_exist_film(client, clear_storage):
    data = client.get('/movies/api/v1.0/get_count_marks/abc/2222')
    assert 'ERROR' in data.get_data(as_text=True)


def test_get_count_marks(client, clear_storage):
    test_create_film(client, clear_storage)
    data = client.get('/movies/api/v1.0/get_count_marks/film/2010')
    assert 'COUNT_MARKS' in data.get_data(as_text=True)


def test_get_not_exist_films_from_substring(client, clear_storage):
    data = client.get('/movies/api/v1.0/get_films/substring/abc')
    assert 'FILMS' in data.get_data(as_text=True)


def test_get_films_from_substring(client, clear_storage):
    test_create_film(client, clear_storage)
    data = client.get('/movies/api/v1.0/get_films/substring/fi')
    assert 'FILMS' in data.get_data(as_text=True)
    assert 'film' in data.get_data(as_text=True)


def test_get_bad_average(client, clear_storage):
    data = client.get('/movies/api/v1.0/get_films/average/badAverage')
    assert 'ERROR' in data.get_data(as_text=True)


def test_get_film_from_average(client, clear_storage):
    test_add_mark_success(client, clear_storage)
    data = client.get('/movies/api/v1.0/get_films/average/5')
    assert 'FILMS' in data.get_data(as_text=True)
    assert 'film' in data.get_data(as_text=True)
