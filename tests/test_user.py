import pytest
from movies.film import Film
from movies.user import User


@pytest.fixture()
def user():
    return User('username', 'password', {})


@pytest.fixture()
def storage():
    return [Film('film', 2010, [], [])]


@pytest.fixture()
def bad_film():
    return Film('NOT_EXIST_FILM', 1000, [], [])


def test_init_user(user):
    assert user.name == 'username'
    assert user.password == 'password'
    assert user.reviews == {}


def test_add_exist_film(storage, user):
    actual = user.add_film('film', 2010, storage)
    assert actual is None


def test_add_film(storage, user):
    actual = user.add_film('FILM', 2010, storage)
    assert isinstance(actual, Film)
    assert actual.name == 'FILM'
    assert actual.year == 2010


@pytest.mark.parametrize('data', [5, 'review'])
def test_add_mark_or_review(storage, user, data):
    actual = user.add_review_or_mark(storage[0], storage, data)
    assert isinstance(actual, Film)
    assert actual.name == 'film'
    assert actual.year == 2010
    if data == 5:
        assert actual.marks == [5]
        assert user.reviews['film' + "2010"] == 5
    else:
        assert actual.reviews == ['review']
        assert user.reviews['film' + "2010"] == 'review'


@pytest.mark.parametrize('data', [-1, 11])
def test_add_bad_mark(storage, user, data):
    actual = user.add_review_or_mark(storage[0], storage, data)
    assert actual is None


@pytest.mark.parametrize('data', [5, 'review'])
def test_add_data_to_empty_film(storage, user, bad_film, data):
    actual = user.add_review_or_mark(bad_film, storage, data)
    assert actual is None
