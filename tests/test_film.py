import pytest
from movies.film import Film


@pytest.fixture()
def film():
    return Film("film", 2010, [], [])


@pytest.fixture()
def film_with_data():
    return Film("film", 2010, [5, 4], ["review1", "review2"])


def test_init_film(film):
    assert film.name == "film"
    assert film.year == 2010


def test_init_film_with_data(film_with_data):
    assert film_with_data.name == "film"
    assert len(film_with_data.marks) == 2
    assert len(film_with_data.reviews) == 2


def test_create_dict(film):
    actual = film.create_dict()
    assert isinstance(actual, dict) is True
    assert actual["name"] == "film"
    assert actual["year"] == 2010


def test_get_average(film, film_with_data):
    actual = film.get_average_mark()
    assert actual == 0
    actual = film_with_data.get_average_mark()
    assert actual == 4.5


def test_get_count_reviews(film_with_data):
    assert film_with_data.get_count_reviews() == 2


def test_get_count_marks(film_with_data):
    assert film_with_data.get_count_marks() == 2
