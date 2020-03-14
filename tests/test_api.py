import pytest
from movies.app import server, find_user, find_film, get_password, add_user
from flask import jsonify, json
from movies.user import User
from movies.film import Film
from unittest.mock import MagicMock


@pytest.fixture()
def client():
    with server.test_client() as client:
        yield client


@pytest.fixture()
def user():
    exist_user = User("name", "qwerty", {})
    not_exist_user = User("NAME", "qwerty", {})
    yield exist_user, not_exist_user


@pytest.fixture()
def user_storage():
    user_storage = [User("name", "qwerty", {})]
    yield user_storage
    user_storage.clear()


@pytest.fixture()
def film_storage():
    film_storage = [Film("film", 2000, [], [])]
    yield film_storage
    film_storage.clear()


@pytest.fixture()
def film():
    exist_film = Film("film", 2000, [], [])
    not_exist_film = Film("FILM", 2000, [], [])
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


def test_add_user(client):
    response = client.post(
        '/movies/api/v1.0/create_account',
        data=json.dumps({"username": "abc", "password": "qwerty"}),
        content_type="application/json"
    )
    data = json.loads(response.get_data())
    assert response.status_code == 200
    assert data["ACTION"] == {"username": "abc"}


def test_add_user_invalid_data(client):
    response = client.post(
        '/movies/api/v1.0/create_account',
        data=json.dumps({"username": "abc"}),
        content_type="application/json"
    )
    data = json.loads(response.get_data())
    assert response.status_code == 400
    assert data["ERROR"] == "Invalid data, please give username and password"


def test_create_film_invalid_data(client, user):
    response = client.post(
        '/movies/api/v1.0/abc/add',
        data=json.dumps({"name": "film"}),
        content_type="application/json"
    )
    data = json.loads(response.get_data())
    assert response.status_code == 400
    assert data["ERROR"] == "Invalid data, please give name and year of film"
