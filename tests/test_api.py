from base64 import b64encode

import pytest
from flask import json
from werkzeug.security import check_password_hash, generate_password_hash
from movies.app import FILM_STORAGE, USER_STORAGE, find_film, find_user, server
from movies.film import Film
from movies.user import User


@pytest.fixture()
def login():
    return "login"


@pytest.fixture()
def password():
    return "password"


@pytest.fixture(autouse=True)
def header(login, password):
    token = b64encode(f'{login}:{password}'.encode()).decode()
    return {'Authorization': f'Basic {token}'}


@pytest.fixture(autouse=True)
def user_auth(login, password):
    USER_STORAGE.append(User("login", generate_password_hash(password), {}))
    return USER_STORAGE


@pytest.fixture(autouse=True)
def clear_storage():
    FILM_STORAGE.clear()
    USER_STORAGE.clear()


@pytest.fixture()
def client():
    with server.test_client() as client:
        yield client


@pytest.fixture()
def user_exist():
    exist_user = User('name', 'qwerty', {})
    yield exist_user


@pytest.fixture()
def user_not_exist():
    not_exist_user = User('NAME', 'qwerty', {})
    yield not_exist_user


@pytest.fixture()
def user_storage(user_exist):
    return [user_exist]


@pytest.fixture()
def film_exist():
    exist_film = Film('film', 2000, [], [])
    yield exist_film


@pytest.fixture()
def film_not_exist():
    not_exist_film = Film('FILM', 2000, [], [])
    yield not_exist_film


@pytest.fixture()
def film_storage(film_exist):
    return [film_exist]


def test_find_not_exist_user(user_not_exist, user_storage):
    with pytest.raises(ValueError):
        find_user(user_not_exist.name, user_storage)


def test_find_user(user_exist, user_storage):
    actual = find_user(user_exist.name, user_storage)
    assert isinstance(actual, User)


def test_find_exist_film(film_not_exist, film_storage):
    with pytest.raises(ValueError):
        find_film(film_not_exist.name, film_not_exist.year, film_storage)


def test_find_film(film_exist, film_storage):
    actual = find_film(film_exist.name, film_exist.year, film_storage)
    assert isinstance(actual, Film)


def test_add_user(client):
    response = client.post(
        '/movies/api/v1.0/create_account',
        data=json.dumps({'username': 'abc', 'password': 'qwerty'}),
        content_type='application/json',
    )
    data = json.loads(response.get_data())
    assert response.status_code == 200
    assert data['ACTION'] == {'username': 'abc'}


def test_add_user_invalid_data(client):
    response = client.post(
        '/movies/api/v1.0/create_account',
        data=json.dumps({'username': 'abc'}),
        content_type='application/json',
    )
    data = json.loads(response.get_data())
    assert response.status_code == 400
    assert data['ERROR'] == 'Invalid data, please give username and password'


def test_create_film_invalid_data(client, header):
    response = client.post(
        '/movies/api/v1.0/login/add',
        headers=header,
        data=json.dumps({'name': 'film'}),
        content_type='application/json',
    )
    data = json.loads(response.get_data())
    assert response.status_code == 400
    assert data['ERROR'] == 'Invalid data, please give name and year of film'


def test_create_film_data(client, header):
    response = client.post(
        '/movies/api/v1.0/bad_login/add',
        headers=header,
        data=json.dumps({'name': 'film', 'year': 2010}),
        content_type='application/json',
    )
    data = json.loads(response.get_data())
    assert response.status_code == 400
    assert data['ERROR'] == 'User does not exist'


def test_create_film(client, header):
    test_add_user(client)
    #   так можно делать? тут я,чтобы пользователя заново не добавлять,
    #   вызываю тестовый метод,который как раз тестирует добавление пользователя
    response = client.post(
        '/movies/api/v1.0/login/add',
        headers=header,
        data=json.dumps({'name': 'film', 'year': 2010}),
        content_type='application/json',
    )
    data = json.loads(response.get_data())
    assert response.status_code == 200
    assert data['FILM'] == {'name': 'film', 'year': 2010}


def test_get_films_empty(client, header):
    data = client.get('/movies/api/v1.0/films', headers=header)
    assert b'LIST OF FILMS' in data.get_data()


def test_get_films(client, header):
    test_create_film(client, header)
    data = client.get('/movies/api/v1.0/films', headers=header)
    assert r'"name":"film"' in data.get_data(as_text=True)
    assert r'"year":2010' in data.get_data(as_text=True)


def test_add_review_invalid_data(client, header):
    response = client.post(
        '/movies/api/v1.0/login/add_review',
        headers=header,
        data=json.dumps({'name': 'film', 'year': 2010}),
        content_type='application/json',
    )
    data = json.loads(response.get_data())
    assert response.status_code == 400
    assert (
        data['ERROR']
        == 'Invalid data, please give name and year of film and your review'
    )


def test_add_review_not_exist_user(client, header):
    response = client.post(
        '/movies/api/v1.0/bad_login/add_review',
        headers=header,
        data=json.dumps({'name': 'film', 'year': 2010, 'review': 'review'}),
        content_type='application/json',
    )
    data = json.loads(response.get_data())
    assert response.status_code == 404
    assert data['ERROR'] == 'User does not exist'


def test_add_review_not_exist_film(client, header):
    test_add_user(client)
    response = client.post(
        '/movies/api/v1.0/login/add_review',
        headers=header,
        data=json.dumps({'name': 'film', 'year': 2010, 'review': 'review'}),
        content_type='application/json',
    )
    data = json.loads(response.get_data())
    assert response.status_code == 404
    assert data['ERROR'] == 'This film does not exist'


def test_add_review_success(client, header):
    test_create_film(client, header)
    response = client.post(
        '/movies/api/v1.0/login/add_review',
        headers=header,
        data=json.dumps({'name': 'film', 'year': 2010, 'review': 'review'}),
        content_type='application/json',
    )
    data = json.loads(response.get_data())
    assert data['ADD_REVIEW'] == {'name': 'film', 'review': 'review'}


def test_add_mark_invalid_data(client, header):
    response = client.post(
        '/movies/api/v1.0/login/add_mark',
        headers=header,
        data=json.dumps({'name': 'film', 'year': 2010}),
        content_type='application/json',
    )
    data = json.loads(response.get_data())
    assert response.status_code == 400
    assert (
        data['ERROR'] == 'Invalid data, please give name and year of film and your mark'
    )


def test_add_mark_not_exist_user(client, header):
    response = client.post(
        '/movies/api/v1.0/bad_login/add_mark',
        headers=header,
        data=json.dumps({'name': 'film', 'year': 2010, 'mark': 5}),
        content_type='application/json',
    )
    data = json.loads(response.get_data())
    assert response.status_code == 404
    assert data['ERROR'] == 'User does not exist'


def test_add_mark_not_exist_film(client, header):
    test_add_user(client)
    response = client.post(
        '/movies/api/v1.0/login/add_mark',
        headers=header,
        data=json.dumps({'name': 'film', 'year': 2010, 'mark': 5}),
        content_type='application/json',
    )
    data = json.loads(response.get_data())
    assert response.status_code == 404
    assert (
        data['ERROR']
        == 'This film does not exist or you mark less 0 or more zero, check it'
    )


def test_add_mark_success(client, header):
    test_create_film(client, header)
    response = client.post(
        '/movies/api/v1.0/login/add_mark',
        headers=header,
        data=json.dumps({'name': 'film', 'year': 2010, 'mark': 5}),
        content_type='application/json',
    )
    data = json.loads(response.get_data())
    assert data['ADD_MARK'] == {'name': 'film', 'mark': 5}


def test_get_average_not_exist_film(client, header):
    data = client.get('/movies/api/v1.0/get_average/abc/2222', headers=header)
    assert 'ERROR' in data.get_data(as_text=True)


def test_get_average(client, header):
    test_create_film(client, header)
    data = client.get('/movies/api/v1.0/get_average/film/2010', headers=header)
    assert 'AVERAGE' in data.get_data(as_text=True)


def test_get_count_reviews_not_exist_film(client, header):
    data = client.get('/movies/api/v1.0/get_count_reviews/abc/2222', headers=header)
    assert 'ERROR' in data.get_data(as_text=True)


def test_get_count_reviews(client, header):
    test_create_film(client, header)
    data = client.get('/movies/api/v1.0/get_count_reviews/film/2010', headers=header)
    assert 'COUNT_REVIEWS' in data.get_data(as_text=True)


def test_get_count_marks_not_exist_film(client, header):
    data = client.get('/movies/api/v1.0/get_count_marks/abc/2222', headers=header)
    assert 'ERROR' in data.get_data(as_text=True)


def test_get_count_marks(client, header):
    test_create_film(client, header)
    data = client.get('/movies/api/v1.0/get_count_marks/film/2010', headers=header)
    assert 'COUNT_MARKS' in data.get_data(as_text=True)


def test_get_not_exist_films_from_substring(client, header):
    data = client.get('/movies/api/v1.0/get_films/substring/abc', headers=header)
    assert 'FILMS' in data.get_data(as_text=True)


def test_get_films_from_substring(client, header):
    test_create_film(client, header)
    data = client.get('/movies/api/v1.0/get_films/substring/fi', headers=header)
    assert 'FILMS' in data.get_data(as_text=True)
    assert 'film' in data.get_data(as_text=True)


def test_get_bad_average(client, header):
    data = client.get('/movies/api/v1.0/get_films/average/badAverage', headers=header)
    assert 'ERROR' in data.get_data(as_text=True)


def test_get_film_from_average(client, header):
    test_add_mark_success(client, header)
    data = client.get('/movies/api/v1.0/get_films/average/5', headers=header)
    assert 'FILMS' in data.get_data(as_text=True)
    assert 'film' in data.get_data(as_text=True)
